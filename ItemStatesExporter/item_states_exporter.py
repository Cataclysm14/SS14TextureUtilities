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
            img = replaceColor(img)
            FolderPath = "Outputs/"+itemName+"_"+str(x)+"x"+str(y)+".rsi"
            tryCreateNestedDir(FolderPath)
            img.save(FolderPath+"/"+stateName+".png")
    yOffset += y*2

shutil.make_archive("sprites", 'zip', "Outputs")

# def exportClothings(dumpFiles=False):
#     resetDir("Outputs")

#     #Fetch camos
#     camoList = os.listdir("Textures")
#     camoDirs = []
#     for camo in camoList:
#         camo = camo.replace(".png","")
#         camo = toPascalCase(camo)
#         camoDirs.append(camo)

#     #Get a list of every template folders.
#     templateList = [x[0] for x in os.walk("Templates")]
#     templateList.pop(0)
#     templateList = [x.replace("Templates\\","") for x in templateList]

#     for camoIndex in range(len(camoList)):
#         camo = camoList[camoIndex]
#         camoPath = camoDirs[camoIndex]
#         camoImg = Image.open("Textures/"+camo)
#         averageCamoColor = getAverageColor("Textures/"+camo)
#         averageCamoColor = (int(averageCamoColor[2]),int(averageCamoColor[1]),int(averageCamoColor[0]))
#         camo = camo.replace(".png","")
#         for clothing in templateList:
#             templateDirectorName = "Templates/" + clothing
#             clothingJson = json.load(open(templateDirectorName+"/params.json"))
#             if "whitelistedCamos" not in clothingJson or camo in clothingJson["whitelistedCamos"]:
#                 if "blacklistedCamos" not in clothingJson or camo not in clothingJson["blacklistedCamos"]:
#                     if dumpFiles:
#                         outputsDirectoryName = "Outputs/"+clothing.replace("CamoName",camo)
#                     else:
#                         outputsDirectoryName = "Outputs/"+clothingJson["path"]+"/"+camoPath+"/"+clothing.replace("CamoName",camo)

#                     #Create the dir
#                     tryCreateNestedDir(outputsDirectoryName)
#                     #Copy the meta.json.
#                     shutil.copy(templateDirectorName+"/meta.json",outputsDirectoryName)
                    
#                     #Apply mask and shading
#                     mask = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_mask.png")
#                     shading = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_shading.png")

#                     img = camoImg.copy()
#                     img = overlayImg(img,mask)
#                     img = overlayImg(img,shading)
#                     img = replaceColor(img)
#                     img = removeAlpha(img)

#                     if os.path.isfile((templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-mask.png")):
#                         bits = replaceColor(Image.new(("RGBA"),(64,64)),(0,0,0,0),(averageCamoColor))
#                         maskBits = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-mask.png")
#                         shadingBits = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-shading.png")
#                         bits = overlayImg(bits,maskBits)
#                         bits = overlayImg(bits,shadingBits)
#                         bits = replaceColor(bits)
#                         bits = removeAlpha(bits)
#                         img = overlayImg(img,bits)

#                     img.save(outputsDirectoryName+"/equipped-"+clothingJson["type"]+".png")
#                     frontSprite = img.crop((0,0,32,32))
#                     backSprite = img.crop((32,0,64,32))
#                     bothSprite = overlayImg(backSprite,frontSprite)

#                     #icon
#                     icon = Image.new("RGBA",(32,32))
#                     offset = (
#                         clothingJson["frontAnchor"][0]-clothingJson["iconOffset"][0],
#                         clothingJson["frontAnchor"][1]-clothingJson["iconOffset"][1]
#                         )
#                     icon = overlayImg(icon,frontSprite,offset)
#                     icon.save(outputsDirectoryName+"/icon"+".png")

#                     #inhand-left
#                     inhandLeft = Image.new("RGBA",(64,64))
#                     for direction in clothingJson["inhandLeftOffset"]:
#                         if direction[2] == "front":
#                             offset = (
#                                 direction[0]-clothingJson["frontAnchor"][0],
#                                 -(direction[1]-clothingJson["frontAnchor"][1])
#                                 )
#                             sprite = frontSprite
#                         elif direction[2] == "back":
#                             offset = (
#                                 direction[0]-clothingJson["backAnchor"][0],
#                                 -(direction[1]-clothingJson["backAnchor"][1])
#                                 )
#                             sprite = backSprite
#                         else:
#                             offset = (
#                                 direction[0]-clothingJson["frontAnchor"][0],
#                                 -(direction[1]-clothingJson["frontAnchor"][1])
#                                 )
#                             sprite = bothSprite
#                         inhandLeft = overlayImg(inhandLeft,sprite,offset)
#                     inhandLeft.save(outputsDirectoryName+"/inhand-left"+".png")
                    
#                     #inhand-right
#                     inhandRight = Image.new("RGBA",(64,64))
#                     for direction in clothingJson["inhandRightOffset"]:
#                         if direction[2] == "front":
#                             offset = (
#                                 direction[0]-clothingJson["frontAnchor"][0],
#                                 -(direction[1]-clothingJson["frontAnchor"][1])
#                                 )
#                             sprite = frontSprite
#                         elif direction[2] == "back":
#                             offset = (
#                                 direction[0]-clothingJson["backAnchor"][0],
#                                 -(direction[1]-clothingJson["backAnchor"][1])
#                                 )
#                             sprite = backSprite
#                         else:
#                             offset = (
#                                 direction[0]-clothingJson["frontAnchor"][0],
#                                 -(direction[1]-clothingJson["frontAnchor"][1])
#                                 )
#                             sprite = bothSprite
#                         inhandRight = overlayImg(inhandRight,sprite,offset)
#                     inhandRight.save(outputsDirectoryName+"/inhand-right"+".png")

# # dumpToggle = input("Dump files?: Y/N >> ")
# # if "Y" in  dumpToggle:
# #     dumpToggle = True
# # else: dumpToggle = False
# # exportClothings(dumpToggle)

# exportClothings()

# # while 0 != 1:
# #     a = 1   