#
# Expense Receipt Extractor
# Created by: Ben Howlett
# Created for: Trillium Advisory Group
# Version: 2.0 
#

from glob import glob
import csv
from urllib import request
from PIL import Image
import os
import PySimpleGUI as sg
import imghdr
import math

class Expense:
    def __init__(self, merchant, customer, name, url):
        self.merchant = merchant.upper().replace("/","_")
        self.customer = customer
        self.name = name
        self.url = url
    
    def get_content_file_extension(self):
        with request.urlopen(self.url) as response:
            info = response.info()
            if info.get_content_subtype() == "pdf":
                return ".pdf"
            elif info.get_content_subtype() == "jpeg":
                return ".jpg"
            elif info.get_content_subtype() == "png":
                return ".png"
            else:
                return "Incompatible File Type"


# Variables for managing UI
files = []
export_folder = ""

# Create the layout as a single column
layout = [
    [
        sg.Text("Welcome to the TAG Expensify Receipt Extractor.\nPlease follow the instructions below to extract receipts from Expensify exports."),
        sg.Push(),
        sg.Image('trillium_logo.png')
    ],
    [
        sg.Text("Select the Expensify export .csv files:"),
        sg.FilesBrowse(target="-REPORT LIST-", key="-SELECT FILES-")
    ],
    [
        sg.Listbox(
            files, enable_events=True, size=(60, 5), key="-REPORT LIST-"
        )
    ],
    [
        sg.Text("Select the folder that you want the PDFs to be exported to::"),
    ],
    [    
        sg.In(size=(53, 1), enable_events=True, key="-EXPORT FOLDER-"),
        sg.FolderBrowse(target="-EXPORT FOLDER-", key="-SELECT FOLDER-")
    ],
    [
        sg.Button("Export Expense Receipts", key="-EXPORT-")
    ]
]


# Create the window
window = sg.Window("Expensify Receipt Extractor", layout)

# Run the event loop
while True:
    event, values = window.read()
    print(event)
    # End loop if the window is closed
    if event == sg.WIN_CLOSED:
        break

    # Get list of files from -SELECT FILES- and populate the -REPORT LIST_
    if event == "-REPORT LIST-":
        files = values["-SELECT FILES-"].split(";")
        file_names = []
        for file in files:
            name = os.path.basename(file)
            file_names.append(name)
        window["-REPORT LIST-"].update(file_names)

    if event == "-EXPORT FOLDER-":
        export_folder = values["-SELECT FOLDER-"]

    if event == "-EXPORT-":
        # Create a list of Expense objects from the files that were selected
        expenses = []

        for file in files:
            with open(file) as csvfile:
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
                firstRow = True
                for row in fileReader:
                    if not firstRow:
                        name = row[27][0:row[27].find('@')].replace('.', ' ').title()
                        customer = row[11][row[11].find(":")+1:len(row[11])]
                        expenses.append(Expense(row[1], customer, name, row[53]))
                    else:
                        firstRow = False
        
        # Download the receipts from the list of Expense instances. Sort PDFs from JPGs and name appropriately
        fileNames = []
        os.mkdir(export_folder + "/Images")

        for expense in expenses:
            if not expense.url == "":
                fileName = expense.name + "_" + expense.customer + "_" + expense.merchant
                print(fileName)
                suffix = fileNames.count(fileName) + 1
                fileNames.append(fileName)
                extension = expense.get_content_file_extension()
                if extension == ".pdf":
                    filePath = export_folder + "/" + fileName + "_" + str(suffix) + extension
                    request.urlretrieve(expense.url, filePath)
                    print ("Receipt saved: " + filePath)
                else:
                    filePath = export_folder + '/Images/' + fileName + "_" + str(suffix) + extension
                    request.urlretrieve(expense.url, filePath)
                    print ("Image saved: " + filePath)
            else:
                print ("Expense does not have a receipt")

        # Convert images to PDFs. Remove the image files 
        for image in glob(export_folder + "/Images/*"):
            # Deal with Windows path formatting
            image = image.replace("\\", "/")
            fileName = os.path.basename(image)
            fileType = imghdr.what(image)
            #print(fileType)

            if fileType == "png" or fileType == "jpeg":
                fileName = fileName.replace("png", "jpg")
                fileName = fileName.replace("jpeg", "jpg")

                tempFile = Image.open(image)
                #x, y = tempFile.size
                #print(x, y)
                #x2, y2 = math.floor(x/2), math.floor(y/2)
                #print(x2, y2)
                #tempFile = tempFile.resize((x2,y2))
                tempRGBFile = tempFile.convert('RGB')
                tempFilePath = export_folder + "/Images/" + fileName
                tempRGBFile.save(tempFilePath, optimize=True, quality=95)

            fileName = fileName.replace("jpg", "pdf")

            # Open the image and convert to PDF
            if fileType == "png":
                newFile = tempRGBFile
            else:
                newFile = Image.open(image)
            newFile.convert('RGB')
            newFile.save(export_folder + "/" + fileName)
            # print ("Receipt saved from image: " + fileName)
            print("tempFilePath: " + tempFilePath)
            # Delete the image file
            if os.path.isfile(image):
                os.remove(image)
            if os.path.isfile(tempFilePath):
                os.remove(tempFilePath)

        # Remove the Images directory
        os.rmdir(export_folder + "/Images")
