import os
import cv2
import numpy as np
import shutil
import re

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
