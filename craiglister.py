from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time
import datetime
import os
import shutil
from inspect import getsourcefile
from os.path import abspath
from gmail import Gmail
from datetime import date
from PIL import Image

gmailUser = ""
gmailPass = ""

#--------------------------------------- Importing Stuff ----------------------

file_path = abspath(getsourcefile(lambda _: None))
file_dir = os.path.normpath(file_path + os.sep + os.pardir)
listingsFolderDirectory = os.path.abspath(os.path.join(file_dir, "listings"))
listedFolderDirectory = os.path.join(listingsFolderDirectory,"listed")
chromedriver = file_dir + "/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

#------------------------------- Set Up Necessary Directories ---------

class listingInfoParse(object):
    def __init__(self,f):
        self.loc = parsing(f,"<Location>").lower()
        self.title = parsing(f,"<Title>")
        self.type = parsing(f,"<Type>")
        self.category = parsing(f,"<Category>")
        self.email = parsing(f,"<Email>")
        self.street = parsing(f,"<Street>")
        self.city = parsing(f,"<City>")
        self.xstreet = parsing(f,"<CrossStreet>")
        self.state = parsing(f,"<State>")
        self.postal = parsing(f,"<Postal>")
        self.body = parsing(f,"<Body>")
        # just get rid of everything that not unicode
        self.body = ''.join([i if ord(i) < 128 else '' for i in self.body])
        # tabs will actually go to the next field in craiglist
        self.body = " ".join(self.body.split("\t"))
        self.price = parsing(f,"<Price>")


#------------------------------  Driver Navigation -----------------

def clickDoneOnImageUploading(listing):
	listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/button").click()

# Don't always have to do this
def clickAbideByGuidelines(listing):
    try:
        listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/div/form/button").click()
    except:
        pass

def clickClassImageUploader(listing):
	listing.driver.find_element_by_id("classic").click()

def clickListingType(listing):
    listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + listing.type + "')]/input").click()

def clickListingCategory(listing):
    listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + listing.category + "')]/input").click()

def uploadImagePath(listing,image):
	listing.driver.find_element_by_xpath(".//*[@id='uploader']/form/input[3]").send_keys(image)

def fillOutListing(listing):
    listing.driver.find_element_by_id("FromEMail").send_keys(listing.email)
    listing.driver.find_element_by_id("ConfirmEMail").send_keys(listing.email)
    listing.driver.find_element_by_id("PostingTitle").send_keys(listing.title)
    listing.driver.find_element_by_id("postal_code").send_keys(listing.postal)
    listing.driver.find_element_by_id("PostingBody").send_keys(listing.body)
    listing.driver.find_element_by_id("Ask").send_keys(listing.price)
    listing.driver.find_element_by_xpath("//*[@id='postingForm']/button").click()

def fillOutGeolocation(listing):
    time.sleep(3)
    listing.driver.find_element_by_id("xstreet0").send_keys(listing.street)
    listing.driver.find_element_by_id("xstreet1").send_keys(listing.xstreet)
    listing.driver.find_element_by_id("city").send_keys(listing.city)
    listing.driver.find_element_by_id("region").send_keys(listing.state)
    time.sleep(1)
    listing.driver.find_element_by_id("search_button").click()
    time.sleep(2)
    #listing.driver.find_element_by_id("postal_code").send_keys(postal) #Should already be there
    listing.driver.find_element_by_xpath("//*[@id='leafletForm']/button[1]").click()

def removeImgExifData(path):
    filename, extension = os.path.splitext(path)
    fullFilename = filename+extension
    image = Image.open(fullFilename)
    data = list(image.getdata())
    imageNoExif = Image.new(image.mode, image.size)
    imageNoExif.putdata(data)
    imageNoExif.save(filename + "copy" + extension)
    os.remove(filename + extension)
    os.rename(filename + "copy" + extension,fullFilename)

def uploadListingImages(listing):
    clickClassImageUploader(listing)
    for image in listing.images:
        removeImgExifData(image)
        uploadImagePath(listing,image)
        time.sleep(5)
    clickDoneOnImageUploading(listing)

def clickAcceptTerms(listing):
    listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/section[1]//button[contains(.,'ACCEPT the terms of use')]").click()

def clickPublishListing(listing):
	listing.driver.find_element_by_xpath("//*[@id='pagecontainer']/section/div[1]/form/button[contains(.,'publish')]").click()

def postListing(listing):
    clickListingType(listing)
    clickListingCategory(listing)
    clickAbideByGuidelines(listing)
    fillOutListing(listing)
    fillOutGeolocation(listing)
    uploadListingImages(listing)
    clickPublishListing(listing)

# --------------------------- Emails ---------------------

def getFirstCraigslistEmailUrl(listing,emails):
    for email in emails:
        email.fetch()
        email.read()
        if listing.title[0:15] in email.subject:
            emailMessage = email.body
            email.archive()
            acceptTermsLink = emailMessage.split("https")
            acceptTermsLink = acceptTermsLink[1].split("\r\n")
            return acceptTermsLink[0]

def acceptTermsAndConditions(listing,termsUrl):
    listing.driver.get("https" + termsUrl)
    clickAcceptTerms(listing)

def acceptEmailTerms(listing):
    gmail = Gmail()
    gmail.login(gmailUser,gmailPass)

    today = date.today()
    year = today.year
    month = today.month
    day = today.day

    time.sleep(120)
    print "Checking email"
    emails = gmail.inbox().mail(sender="robot@craigslist.org",unread=True,after=datetime.date(year, month, day-1))
    termsUrl = getFirstCraigslistEmailUrl(listing,emails)
    acceptTermsAndConditions(listing,termsUrl)

    gmail.logout()
    print "Done Checking Email"


# --------------------------- Craigslist Posting Actions ---------------

def moveFolder(folder,listedFolderDirectory):

    now = time.strftime("%c")

    # %x >>>get the date like this 7/16/2014
    today_dir = os.path.join(listedFolderDirectory,time.strftime("%x").replace("/","-"))

    # Make todays date under the listed directory
    makeFolder(today_dir)

    # Move the folder to the listed todays date directory
    shutil.move(folder, today_dir)

def parsing(f,splits):
    fsplit = f.split(splits)
    return fsplit[1]


# If more than 24 hours passed will look like
# 1 day, 13:37:47.356000
def hasItBeenXDaysSinceFolderListed(folder,x):
    dateSplit = folder.split('-')
    folderDate = datetime.date(int(dateSplit[2]) + 2000, int(dateSplit[0]), int(dateSplit[1]))
    currentDatetime = datetime.datetime.now()
    folderTimePassed = currentDatetime - datetime.datetime.combine(folderDate, datetime.time())
    if "day" not in str(folderTimePassed):
        return False
    daysPassed = str(folderTimePassed).split('day')[0]
    if int(daysPassed.strip()) >= x:
        return True
    return False

def getOrderedListingImages(listingFolder):
    print 'listingFolder',listingFolder
    listingImages = [f for f in os.listdir(listingFolder) if os.path.isfile(os.path.join(listingFolder,f)) and f[0] != '.'  and f != 'info.txt' ]
    print 'listingImages',listingImages
    secondList = [os.path.abspath(os.path.join(listingFolder, x)) for x in listingImages if (x[1] != "_") or (x[0].isdigit() == False) and x[0] != '.']
    firstList = [os.path.abspath(os.path.join(listingFolder, x)) for x in listingImages if (x[1] == "_") and (x[0].isdigit()) and x[0] != '.']

    firstList.sort()
    secondList.sort()

    orderedListingImages = []
    for x in firstList:orderedListingImages.append(x)
    for x in secondList:orderedListingImages.append(x)
    return orderedListingImages

# Get all the date folders of listed items
listedItemsFolders = [folder for folder in os.listdir(listedFolderDirectory) if folder[0] != "."]

# Moving items that are 3 days or older back into the queue to get listed again
for dayListedFolder in listedItemsFolders:

    if (hasItBeenXDaysSinceFolderListed(dayListedFolder,3) == False):
        continue

    listedFolders = [listedFolders for listedFolders in os.listdir(os.path.join(listedFolderDirectory,dayListedFolder)) if listedFolders[0] != "."]
    dayListedFolderDirectory = os.path.join(listedFolderDirectory,dayListedFolder)

    for listedFolder in listedFolders:
        theListedFolderDirectory = os.path.join(dayListedFolderDirectory,listedFolder)
        shutil.move(theListedFolderDirectory,listingsFolderDirectory)
    shutil.rmtree(dayListedFolderDirectory)


# List Items
listingFolders = [listing for listing in os.listdir(listingsFolderDirectory) if listing[0] != "." and listing != "listed"]

for listingFolder in listingFolders:
    listingFolder = os.path.abspath(os.path.join(listingsFolderDirectory, listingFolder))
    with open(os.path.abspath(os.path.join(listingFolder, 'info.txt')), 'r') as info:
        listing = listingInfoParse(info.read())
    listing.images = getOrderedListingImages(listingFolder)
    listing.driver = webdriver.Chrome(chromedriver)
    listing.driver.get("https://post.craigslist.org/c/" + listing.loc + "?lang=en")
    postListing(listing)
    acceptEmailTerms(listing)
    moveFolder(listingFolder,listedFolderDirectory)
    listing.driver.close()
    time.sleep(120)
    print "Waiting 2 minutes"
print "No More Craiglist Items To List"
