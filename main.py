from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QListWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QListWidgetItem
from PyQt5 import QtCore
from datetime import datetime
import time
from shutil import copyfile
from PIL import Image
import requests
import vdf
import os

games = None

lastCreation = None

imgIndex = 1

def openFile(label):
    fileName = QFileDialog.getOpenFileName()
    global chosenImage
    chosenImage = fileName[0]
    if(fileName[0] != ""):
        label.setText(fileName[0].split('/')[-1])

def searchGame(gameName, qlist):
    if(gameName == ""):
        return

    qlist.clear()

    global games
    if games is None:
        games = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/?format=json').json()["applist"]["apps"]
    for game in games:
        if gameName.lower() in game["name"].lower():
            item = QListWidgetItem(str(game["name"]))
            item.setData(QtCore.Qt.UserRole, str(game["appid"]))
            qlist.addItem(item)

def itemSelected(item):
    gameLabel.setText(item.text())
    global chosenGame
    chosenGame = str(item.data(QtCore.Qt.UserRole))

def createImage():
    global chosenImage, chosenGame

    if chosenGame is None or (chosenImage == "") or not os.path.isdir(dirBox.text()):
        return
    
    creationDate = datetime.today()

    global lastCreation

    if lastCreation is None:
        lastCreation = creationDate
    elif lastCreation.strftime('%Y%m%d%H%M%S') == creationDate.strftime('%Y%m%d%H%M%S'):
        global imgIndex
        imgIndex = imgIndex + 1
    else:
        lastCreation = creationDate

    unixTime = int(time.mktime(creationDate.timetuple()))
    imgName = creationDate.strftime('%Y%m%d%H%M%S') + "_" + str(imgIndex) + ".jpg"

    defaultDir = dirBox.text() + "/760/"

    img = Image.open(chosenImage)

    vdfDir = defaultDir + "screenshots.vdf"

    parsedVdf = vdf.parse(open(vdfDir))

    if not os.path.isdir(defaultDir):
        os.makedirs(defaultDir)
        os.makedirs(defaultDir + "remote")
    elif not os.path.isdir(defaultDir + "remote/" + str(chosenGame)):
        parsedVdf["screenshots"][str(chosenGame)] = {}
        os.makedirs(defaultDir + "remote/" + str(chosenGame))
        os.makedirs(defaultDir + "remote/" + str(chosenGame) + "/screenshots")
        os.makedirs(defaultDir + "remote/" + str(chosenGame) + "/screenshots/thumbnails")

    imgPath = defaultDir + 'remote/' + str(chosenGame) + "/screenshots"
    
    imgSavePath = imgPath + "/" + imgName

    imgWidth = img.size[0]
    imgHeight = img.size[1]
    thumbHeight = (200 * imgHeight) / imgWidth

    if(chosenImage.split('.')[-1].lower() == "jpg" or chosenImage.split('.')[-1].lower() == "jpeg"):
        copyfile(chosenImage, imgSavePath)
    else:
        img = img.convert('RGB')
        imgSave = img.save(imgSavePath, quality=95)

    size = 200, thumbHeight

    thumbSavePath = imgPath + "/thumbnails/" + imgName

    imgThumb = img
    imgThumb.thumbnail(size)
    imgThumb.save(thumbSavePath)

    lastKey = 0
    newKey = 0

    if len(list(parsedVdf["screenshots"][str(chosenGame)])) != 0:
        lastKey = int(list(parsedVdf["screenshots"][str(chosenGame)])[-1])
        newKey = lastKey + 1

    parsedVdf["screenshots"][str(chosenGame)][str(newKey)] = {
        "type":"1",
        "filename": str(chosenGame) + "/screenshots/" + imgName,
        "thumbnail": str(chosenGame) + "/screenshots/thumbnails/" + imgName,
        "vrfilename":"",
        "imported":"1",
        "width": str(imgWidth),
        "height": str(imgHeight),
        "gameid": str(chosenGame),
        "creation": str(unixTime),
        "caption":"",
        "Permissions":"2",
        "hscreenshot":"18446744073709551615"
    }

    vdf.dump(parsedVdf, open(vdfDir,'w'), pretty=True)

app = QApplication([])
window = QWidget()

window.setWindowTitle('Steam Screenshot Creator')

searchBox = QLineEdit()
dirBox = QLineEdit()

gameButton = QPushButton('Search for game')
imgButton = QPushButton('Select image')
createButton = QPushButton('Create screenshot')

imgLabel = QLabel("No image selected")
gameSLabel = QLabel('Select a game:')
gameLabel = QLabel("No game selected")
dirLabel = QLabel("User folder directory\ne.g.: C:/Program Files (x86)/Steam/userdata/97068767")
dirLabel.setWordWrap(True)

chosenGame = None

chosenImage = ''

applist = QListWidget()

applist.itemActivated.connect(itemSelected)

imgButton.clicked.connect(lambda: openFile(imgLabel))
gameButton.clicked.connect(lambda: searchGame(searchBox.text(), applist))
createButton.clicked.connect(createImage)

windowLayout = QVBoxLayout(window)

windowLayout.addWidget(dirLabel)
windowLayout.addWidget(dirBox)
windowLayout.addWidget(imgLabel)
windowLayout.addWidget(gameLabel)
windowLayout.addWidget(imgButton)
windowLayout.addWidget(gameSLabel)
windowLayout.addWidget(searchBox)
windowLayout.addWidget(applist)
windowLayout.addWidget(gameButton)
windowLayout.addWidget(createButton)

window.setLayout(windowLayout)

window.setMinimumWidth(300)

window.show()

app.exec_()