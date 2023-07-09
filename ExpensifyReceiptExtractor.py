from glob import glob
import csv
from urllib import request
from PIL import Image

class Expense:
    def __init__(self, merchant, customer, name, url):
        self.merchant = merchant
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
            else:
                return "Incompatible File Type"


expenses = []

for file in glob("Expense Exports/*.csv"):
    with open(file) as csvfile:
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        firstRow = True
        for row in fileReader:
            if not firstRow:
                #name = row[27][0:row[27].find('.')].capitalize() + " " + row[27][row[27].find('.')+1:row[27].find('@')].capitalize()
                name = row[27][0:row[27].find('@')].replace('.', ' ').title()
                customer = row[11][row[11].find(":")+1:len(row[11])]
                expenses.append(Expense(row[1], customer, name, row[53]))
            else:
                firstRow = False

fileNames = []

for expense in expenses:
     fileName = expense.name + "_" + expense.customer + "_" + expense.merchant
     suffix = fileNames.count(fileName) + 1
     fileNames.append(fileName)
     extension = expense.get_content_file_extension()
     if extension == ".pdf":
        filePath = 'PDFs/' + fileName + "_" + str(suffix) + extension
        request.urlretrieve(expense.url, filePath)
        print ("Receipt saved: " + filePath)
     elif extension == ".jpg":
        filePath = 'Images/' + fileName + "_" + str(suffix) + extension
        request.urlretrieve(expense.url, filePath)
        print ("Image saved: " + filePath)

for image in glob("Images/*.jpg"):
    image = image.replace("\\", "/")
    fileName = image[image.find('/')+1:len(image)-4] + ".pdf"
    newFile = Image.open(image)
    newFile.convert('RGB')
    newFile.save('PDFs/' + fileName)
    print ("Receipt saved from image: " + fileName)

print ("Receipt extraction complete.")