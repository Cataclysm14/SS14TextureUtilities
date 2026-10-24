import os
import shutil
import re
import numpy as np
import cv2
import pprint
from PIL import Image #in cmd enter "py -m pip download pillow" + "py -m pip install pillow", works for me, probably not on other devices :godo:

import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def replaceColor(img,oldColor=(255,0,0,255),newColor=(0,0,0,0)):
    #Too lazy to use channels.
    img_pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if img_pixels[x,y] == oldColor:
                img_pixels[x,y] = newColor
    return img

def getAverageColor(path):
    img = cv2.imread(path)
    averagePerRow = np.average(img, axis=0)
    average = np.average(averagePerRow, axis=0)
    return average

def removeAlpha(img):
    #Too lazy to use channels.
    img_pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if img_pixels[x,y][3] != 255 and not img_pixels[x,y][3] == 0:
                img_pixels[x,y] = (img_pixels[x,y][0],img_pixels[x,y][1],img_pixels[x,y][2],255)
    return img

def overlayImg(img,mask,offset=(0,0)):
    img.paste(mask, (offset[0],-offset[1]), mask)
    return img

def tryCreateDir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

def tryDeleteDir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def resetDir(directory):
    tryDeleteDir(directory)
    os.mkdir(directory)

def tryCreateNestedDir(directory):
    directoryList = directory.split("/")
    folder = ""
    for folderIndex in range(len(directoryList)):
        folder = folder + directoryList[folderIndex] + "/"
        tryCreateDir(folder)

def toPascalCase(string):
    return re.sub(r"(^|_)([a-z])", lambda match: match.group(2).upper(), string)

def strToCoords(string):
    return (int(string.split(",")[0]),int(string.split(",")[1]))

ScrubbedColors=(
(255,0,143,255),#head
(255,101,0,255),#torso
(0,255,0,255),#Larm
(255,192,72,255),#Lhand
(144,68,255,255),#Rarm
(0,239,255,255),#Rhand
(255,0,0,255),#Lleg
(255,255,0,255),#Lfoot
(216,171,255,255),#Rleg
(0,76,255,255),#Rfoot
(255,0,0,255),#Legacy
)

Sheet = Image.open("Items.png")

Parameters = yaml.load(open("params.yml"),Loader)
pprint.pp(Parameters)

resetDir("Outputs")
yOffset = 0
for item in Parameters:
    xOffset = 0
    itemName = list(item.keys())[0]
    for states in item.values():
        for state in states:
            stateName = list(state.keys())[0]
            stateParams = list(state.values())
            size = strToCoords(list((stateParams[0][0]).values())[0])
            directional = list((stateParams[0][1]).values())[0]
            x = size[0]
            y = size[1]
            if directional:
                img = Sheet.crop((xOffset,yOffset,xOffset+x*2,yOffset+y*2))
                xOffset += x*2
            else:
                img = Sheet.crop((xOffset,yOffset,xOffset+x,yOffset+y))
                xOffset += x
            for color in ScrubbedColors:
                img = replaceColor(img,color)
            FolderPath = "Outputs/"+itemName+"_"+str(x)+"x"+str(y)+".rsi"
            tryCreateNestedDir(FolderPath)
            img.save(FolderPath+"/"+stateName+".png")
    yOffset += y*2

shutil.make_archive("sprites", 'zip', "Outputs")