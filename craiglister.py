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
posts_dir = os.path.abspath(os.path.join(file_dir, "posts"))
posted_dir = os.path.join(posts_dir,"posted")
chromedriver = file_dir + "/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

#-------------------------------------- Current Directory Stuff

example = """
<Location><Location>
<Title><Title>
<Type><Type>
<Category><Category>
<Email><Email>
<Street><Street>
<City><City>
<CrossStreet><CrossStreet>
<State><State>
<Postal><Postal>
<Body><Body>
<Price><Price>

// Categories
	// Types

//job offered
//gig offered (I'm hiring for a short-term, small or odd job)
//resume / job wanted
//housing offered
//housing wanted
//for sale by owner
	//antiques - by owner
	//appliances - by owner
	//arts & crafts - by owner
	//atvs, utvs, snowmobiles - by owner
	//auto parts - by owner
	//baby & kid stuff - by owner (no illegal sales of recall items, e.g. drop-side cribs)
	//barter
	//bicycle parts & accessories - by owner
	//bicycles - by owner
	//boats - by owner
	//books & magazines - by owner
	//business/commercial - by owner
	//cars & trucks - by owner
	//cds / dvds / vhs - by owner (no pornography please)
	//cell phones - by owner
	//clothing & accessories - by owner
	//collectibles - by owner
	//computer parts & accessories - by owner
	//computers - by owner
	//electronics - by owner
	//farm & garden - by owner (legal sales of agricultural livestock OK)
	//free stuff (no "wanted" ads, pets, promotional giveaways, or intangible/digital items please)
	//furniture - by owner
	//garage & moving sales (no online or virtual sales here please)
	//general for sale - by owner
	//health and beauty - by owner
	//heavy equipment - by owner
	//household items - by owner
	//jewelry - by owner
	//materials - by owner
	//motorcycle parts & accessories - by owner
	//motorcycles/scooters - by owner
	//musical instruments - by owner
	//photo/video - by owner
	//rvs - by owner
	//sporting goods - by owner (no firearms, ammunition, pellet/BB guns, stun guns, etc)
	//tickets - by owner (please do not sell tickets for more than face value)
	//tools - by owner
	//toys & games - by owner
	//video gaming - by owner
	//wanted - by owner
//for sale by dealer
//wanted by owner
//wanted by dealer
//service offered
//personal / romance
//community
//event / class
"""

readme = """
In the posts folder create a new folder that describes the item to post
For example make a folder Guitar
Then copy exampleinfo.txt into the Guitar folder and rename info.txt
File out the info.txt with the correct craigslist information
Put any pictures you want in the listing in the Guitar folder
You can change the order of the images by naming appending _1 _2 _3 etc.
"""

# Make a file with the example format
with open(os.path.join(file_dir,"exampleinfo.txt"),"w") as f:
	f.write(example)
	f.close()

# Make a file with the example format
with open(os.path.join(file_dir,"README.txt"),"w") as f:
	f.write(readme)
	f.close()
	
#---------------------------------- Set Up Readme and Example ----------------

def makeFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
# Make the posted folder
makeFolder(posted_dir)

#------------------------------- Set Up Necessary Directories ---------

class post(object):
    def __init__(self,f):
        self.loc = parsing(f,"<Location>").lower()
        self.title = parsing(f,"<Title>")
        self.types = parsing(f,"<Type>")
        self.cat = parsing(f,"<Category>")
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


#------------------------------ Post Object ----------------------------


def abide_by_guidelines(driver):
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/div/form/button")

def post_type(driver,label):
    #for sale by dealer
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + label + "')]/input")


def post_category(driver,label):
    #furniture - by dealer
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + label + "')]/input")

def create_post(driver,p):
    driver.find_element_by_id("FromEMail").send_keys(p.email)
    driver.find_element_by_id("ConfirmEMail").send_keys(p.email)
    driver.find_element_by_id("PostingTitle").send_keys(p.title)
    driver.find_element_by_id("postal_code").send_keys(p.postal)
    driver.find_element_by_id("PostingBody").send_keys(p.body)
    driver.find_element_by_id("Ask").send_keys(p.price)
    driver.find_element_by_xpath("//*[@id='postingForm']/button").click()

def geo_location(driver,p):
    time.sleep(3)
    driver.find_element_by_id("xstreet0").send_keys(p.street)
    driver.find_element_by_id("xstreet1").send_keys(p.xstreet)
    driver.find_element_by_id("city").send_keys(p.city)
    driver.find_element_by_id("region").send_keys(p.state)
    time.sleep(1)
    driver.find_element_by_id("search_button").click()
    time.sleep(2)
    #driver.find_element_by_id("postal_code").send_keys(postal) #Should already be there
    driver.find_element_by_xpath("//*[@id='leafletForm']/button[1]").click()

def removeImgData(path):
    filename, ext = os.path.splitext(path)
    image = Image.open(filename+ext)
    print "Striping Images of Data"
    # Strip the exif data
    data = list(image.getdata())
    imageNoExif = Image.new(image.mode, image.size)
    imageNoExif.putdata(data)
    imageNoExif.save(filename + "copy" + ext)
    os.remove(filename + ext)
    os.rename(filename + "copy" + ext,filename+ext)

def add_images(driver,p):
    driver.find_element_by_id("classic").click()
    for x in p:
        removeImgData(x)
        driver.find_element_by_xpath(".//*[@id='uploader']/form/input[3]").send_keys(x)
        time.sleep(5)

    # Click done wtih images button
    driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/button").click()

def accept_terms(driver):
    driver.find_element_by_xpath("//*[@id='pagecontainer']/section/section[1]//button[contains(.,'ACCEPT the terms of use')]").click()

def publish(driver):
    driver.find_element_by_xpath("//*[@id='pagecontainer']/section/div[1]/form/button[contains(.,'publish')]").click()
    

# --------------------------- Craigslist Posting Actions ---------------

def moveFolder(folder,posted_dir):
    
    now = time.strftime("%c")
    
    # %x >>>get the date like this 7/16/2014
    today_dir = os.path.join(posted_dir,time.strftime("%x").replace("/","-"))
    
    # Make todays date under the posted directory
    makeFolder(today_dir)
    
    # Move the folder to the posted todays date directory
    shutil.move(folder, today_dir)


    
def parsing(f,splits):
    fsplit = f.split(splits)
    return fsplit[1]


# Get all the date folders of posted items
date_folders = [child for child in os.listdir(posted_dir) if child[0] != "."]

# Moving items that are 3 days or older back into the queue to get posted
for x in date_folders:
    print x
    date_split = x.split('-')
    folder_date = datetime.date(int(date_split[2]) + 2000, int(date_split[0]), int(date_split[1]))
    now = datetime.datetime.now()
    days_passed = now - datetime.datetime.combine(folder_date, datetime.time())

    # If more than 24 hours passed will look like
    # 1 day, 13:37:47.356000
    if "day" in str(days_passed):
        days_split = str(days_passed).split('day')

        # The amount of days that have passed
        if int(days_split[0].strip()) >= 3:

            # Repost the craigslist ads
            # To do that we can just move the folders back into the main folder :D
            listings_array = [child for child in os.listdir(os.path.join(posted_dir,x)) if child[0] != "."]

            date_folder_dir = os.path.join(posted_dir,x)
            
            for y in listings_array:
                listing_dir = os.path.join(date_folder_dir,y)

                # Move the listing folder to the posts directory
                shutil.move(listing_dir,posts_dir)
                

            shutil.rmtree(date_folder_dir)

#-------------------------- Dealing with posted listings --------------------


# Get all the folders we are needing to post  
folders = [child for child in os.listdir(posts_dir) if child[0] != "."]

# Don't include the posted folder in our listings folder
folders.pop(folders.index("posted"))

print folders
                          
for folder in folders:

    # The absolue path to the folder we are using
    folder = os.path.abspath(os.path.join(posts_dir, folder))

    print folder
    
    # Gets all the files in the folder
    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and f[0] != '.' ]

    print onlyfiles
    # Deletes the text file from our image array
    onlyfiles.pop(onlyfiles.index("info.txt"))

    # Basically I want to sort things with numbered prefixes and use them first
    # Then use the other images
    # I could use zip and such but I don't have the function handy that works well
    sec_list = [os.path.abspath(os.path.join(folder, x)) for x in onlyfiles if (x[1] != "_") or (x[0].isdigit() == False) and x[0] != '.']
    first_list = [os.path.abspath(os.path.join(folder, x)) for x in onlyfiles if (x[1] == "_") and (x[0].isdigit()) and x[0] != '.']

    first_list.sort()
    sec_list.sort()

    allpics = []
    for x in first_list:allpics.append(x)
    for x in sec_list:allpics.append(x)

    # Opens the info file
    with open(os.path.abspath(os.path.join(folder, 'info.txt')), 'r') as info:

        # Parses the info file
        p = post(info.read())

    print "Opening browser"
    # Create a new instance of the Firefox driver
    driver = webdriver.Chrome(chromedriver)

    # Go to craigslist postpage
    driver.get("https://post.craigslist.org/c/" + p.loc + "?lang=en")

    print "Opened"
    post_type(driver,p.types).click()
    post_category(driver,p.cat).click()
    print "Chose category"
    try:
        abide_by_guidelines(driver).click() # Don't always have to do this for some reason
    except:
        pass
    create_post(driver,p)
    
    geo_location(driver,p)
    add_images(driver,allpics)
    print "Adding Images"
    publish(driver)
    print "Publishing Listing"
    g = Gmail()
    g.login(gmailUser,gmailPass)
    
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    time.sleep(120)
    print "Checking email"
    emails = g.inbox().mail(sender="robot@craigslist.org",unread=True,after=datetime.date(year, month, day-1))
    for email in emails:
        email.fetch()
        email.read()
        if p.title[0:15] in email.subject:
            eMessage = email.body
            msg = eMessage.split("https")
            msg = msg[1].split("\r\n")
            msg = msg[0]
            driver.get("https" + msg)
            accept_terms(driver)
            moveFolder(folder,posted_dir)
            email.delete()
            break
    g.logout()
    print "Done Checking Emails"
    driver.close()
    time.sleep(120)
    

#------------------ Dealing with posts that need to be posted ------------------
