import os
import shutil
import json
import re
import numpy as np
import cv2
from PIL import Image #in cmd enter "py -m pip download pillow" + "py -m pip install pillow", works for me, probably not on other devices :godo:

import utils

modulePath = "TextureClothingMaker/"

def exportClothings(dumpFiles=False):
    utils.resetDir(modulePath+"Outputs")

    #Fetch camos
    camoList = os.listdir(modulePath+"Textures")
    camoDirs = []
    for camo in camoList:
        camo = camo.replace(".png","")
        camo = utils.toPascalCase(camo)
        camoDirs.append(camo)

    #Get a list of every template folders.
    templateList = [x[0] for x in os.walk(modulePath+"Templates")]
    templateList.pop(0)
    templateList = [x.replace(modulePath+"Templates\\","") for x in templateList]

    for camoIndex in range(len(camoList)):
        camo = camoList[camoIndex]
        camoPath = camoDirs[camoIndex]
        camoImg = Image.open(modulePath+"Textures/"+camo)
        averageCamoColor = utils.getAverageColor(modulePath+"Textures/"+camo)
        averageCamoColor = (int(averageCamoColor[2]),int(averageCamoColor[1]),int(averageCamoColor[0]))
        camo = camo.replace(".png","")
        for clothing in templateList:
            templateDirectorName = modulePath + "Templates/" + clothing
            clothingJson = json.load(open(templateDirectorName+"/params.json"))
            if "whitelistedCamos" not in clothingJson or camo in clothingJson["whitelistedCamos"]:
                if "blacklistedCamos" not in clothingJson or camo not in clothingJson["blacklistedCamos"]:
                    if dumpFiles:
                        outputsDirectoryName = modulePath+"Outputs/"+clothing.replace("CamoName",camo)
                    else:
                        outputsDirectoryName = modulePath+"Outputs/"+clothingJson["path"]+"/"+camoPath+"/"+clothing.replace("CamoName",camo)

                    #Create the dir
                    utils.tryCreateNestedDir(outputsDirectoryName)
                    #Copy the meta.json.
                    shutil.copy(templateDirectorName+"/meta.json",outputsDirectoryName)
                    
                    #Apply mask and shading
                    mask = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_mask.png")
                    shading = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_shading.png")

                    img = camoImg.copy()
                    img = utils.overlayImg(img,mask)
                    img = utils.overlayImg(img,shading)
                    img = utils.replaceColor(img)
                    img = utils.removeAlpha(img)

                    if os.path.isfile((templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-mask.png")):
                        bits = utils.replaceColor(Image.new(("RGBA"),(64,64)),(0,0,0,0),(averageCamoColor))
                        maskBits = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-mask.png")
                        shadingBits = Image.open(templateDirectorName+"/equipped-"+clothingJson["type"]+"_bits-shading.png")
                        bits = utils.overlayImg(bits,maskBits)
                        bits = utils.overlayImg(bits,shadingBits)
                        bits = utils.replaceColor(bits)
                        bits = utils.removeAlpha(bits)
                        img = utils.overlayImg(img,bits)

                    img.save(outputsDirectoryName+"/equipped-"+clothingJson["type"]+".png")
                    frontSprite = img.crop((0,0,32,32))
                    backSprite = img.crop((32,0,64,32))
                    bothSprite = utils.overlayImg(backSprite,frontSprite)

                    #icon
                    icon = Image.new("RGBA",(32,32))
                    offset = (
                        clothingJson["frontAnchor"][0]-clothingJson["iconOffset"][0],
                        clothingJson["frontAnchor"][1]-clothingJson["iconOffset"][1]
                        )
                    icon = utils.overlayImg(icon,frontSprite,offset)
                    icon.save(outputsDirectoryName+"/icon"+".png")

                    #inhand-left
                    inhandLeft = Image.new("RGBA",(64,64))
                    for direction in clothingJson["inhandLeftOffset"]:
                        if direction[2] == "front":
                            offset = (
                                direction[0]-clothingJson["frontAnchor"][0],
                                -(direction[1]-clothingJson["frontAnchor"][1])
                                )
                            sprite = frontSprite
                        elif direction[2] == "back":
                            offset = (
                                direction[0]-clothingJson["backAnchor"][0],
                                -(direction[1]-clothingJson["backAnchor"][1])
                                )
                            sprite = backSprite
                        else:
                            offset = (
                                direction[0]-clothingJson["frontAnchor"][0],
                                -(direction[1]-clothingJson["frontAnchor"][1])
                                )
                            sprite = bothSprite
                        inhandLeft = utils.overlayImg(inhandLeft,sprite,offset)
                    inhandLeft.save(outputsDirectoryName+"/inhand-left"+".png")
                    
                    #inhand-right
                    inhandRight = Image.new("RGBA",(64,64))
                    for direction in clothingJson["inhandRightOffset"]:
                        if direction[2] == "front":
                            offset = (
                                direction[0]-clothingJson["frontAnchor"][0],
                                -(direction[1]-clothingJson["frontAnchor"][1])
                                )
                            sprite = frontSprite
                        elif direction[2] == "back":
                            offset = (
                                direction[0]-clothingJson["backAnchor"][0],
                                -(direction[1]-clothingJson["backAnchor"][1])
                                )
                            sprite = backSprite
                        else:
                            offset = (
                                direction[0]-clothingJson["frontAnchor"][0],
                                -(direction[1]-clothingJson["frontAnchor"][1])
                                )
                            sprite = bothSprite
                        inhandRight = utils.overlayImg(inhandRight,sprite,offset)
                    inhandRight.save(outputsDirectoryName+"/inhand-right"+".png")

# dumpToggle = input("Dump files?: Y/N >> ")
# if "Y" in  dumpToggle:
#     dumpToggle = True
# else: dumpToggle = False
# exportClothings(dumpToggle)

exportClothings()

# while 0 != 1:
#     a = 1   