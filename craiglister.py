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

file_path = abspath(getsourcefile(lambda _: None))
file_dir = os.path.normpath(file_path + os.sep + os.pardir)

def post_type(driver,label):
    #for sale by dealer
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + label + "')]/input")

def abide_by_guidelines(driver):
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/div/form/button")

def post_category(driver,label):
    #furniture - by dealer
    return driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/blockquote//label[contains(.,'" + label + "')]/input")

def create_post(driver,email,title,body,postal_code,price=""):
    driver.find_element_by_id("FromEMail").send_keys(email)
    driver.find_element_by_id("ConfirmEMail").send_keys(email)
    driver.find_element_by_id("PostingTitle").send_keys(title)
    driver.find_element_by_id("postal_code").send_keys(postal_code)
    driver.find_element_by_id("PostingBody").send_keys(body)
    driver.find_element_by_id("Ask").send_keys(price)
    driver.find_element_by_xpath("//*[@id='postingForm']/button").click()

def geo_location(driver,street="",cross_street="",city="",state="",postal=""):
    time.sleep(3)
    driver.find_element_by_id("xstreet0").send_keys(street)
    driver.find_element_by_id("xstreet1").send_keys(cross_street)
    driver.find_element_by_id("city").send_keys(city)
    driver.find_element_by_id("region").send_keys(state)
    time.sleep(1)
    driver.find_element_by_id("search_button").click()
    time.sleep(2)
    #driver.find_element_by_id("postal_code").send_keys(postal) #Should already be there
    driver.find_element_by_xpath("//*[@id='leafletForm']/button[1]").click()
    
def add_images(driver,p):
    driver.find_element_by_id("classic").click()
    for x in p:
        driver.find_element_by_xpath(".//*[@id='uploader']/form/input[3]").send_keys(x)
        time.sleep(5)

    # Click done wtih images button
    driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/button").click()

def moveFolder(folder,posted_dir):
    
    now = time.strftime("%c")
    
    #>>>get the date like this 7/16/2014
    today_dir = os.path.join(posted_dir,time.strftime("%x"))
    today_dir = today_dir.replace("/","-")
    print today_dir
    
    # Make todays date under the posted directory
    makeFolder(today_dir)
    
    # Move the folder to the posted todays date directory
    shutil.move(folder, today_dir)

def makeFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
def parsing(f,splits):
    fsplit = f.split(splits)
    return fsplit[1]

def parse_text_file(ft):
    f = ft.read()
    loc = parsing(f,"<Location>")
    title = parsing(f,"<Title>")
    types = parsing(f,"<Type>")
    cat = parsing(f,"<Category>")
    email = parsing(f,"<Email>")
    street = parsing(f,"<Street>")
    city = parsing(f,"<City>")
    xstreet = parsing(f,"<CrossStreet>")
    state = parsing(f,"<State>")
    postal = parsing(f,"<Postal>")
    body = parsing(f,"<Body>")

    # just get rid of everything that not unicode
    body = ''.join([i if ord(i) < 128 else '' for i in body])

    # tabs will actually go to the next field in craiglist
    body = " ".join(body.split("\t"))
    
    price = parsing(f,"<Price>")
    return loc.lower(),title,types,cat,email,street,xstreet,state,postal,body,city,price


posts_dir = os.path.abspath(os.path.join(file_dir, "posts"))
posted_dir = os.path.join(posts_dir,"posted")

# Make the posted folder
makeFolder(posted_dir)

example = """
<Location><Location>
<Title><Title>
<Type><Type>
<Category><Category>
<Email><Email>
<Street><Street>
<City>Ames<City>
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
print os.path.join(file_dir,"exampleinfo.txt")

with open(os.path.join(file_dir,"exampleinfo.txt"),"w") as f:
	f.write(example)
	f.close()

# Get all the date folders of posted items
date_folders = [child for child in os.listdir(posted_dir)]

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
            listings_array = [child for child in os.listdir(os.path.join(posted_dir,x))]

            date_folder_dir = os.path.join(posted_dir,x)
            
            for y in listings_array:
                listing_dir = os.path.join(date_folder_dir,y)

                # Move the listing folder to the posts directory
                shutil.move(listing_dir,posts_dir)

            os.rmdir(date_folder_dir)
        
folders = [child for child in os.listdir(posts_dir)]

# Don't include the posted folder in our listings folder
folders.pop(folders.index("posted"))

print folders
                          
for folder in folders:

    # The absolue path to the folder we are using
    folder = os.path.abspath(os.path.join(posts_dir, folder))
                          
    # Gets all the files in the folder
    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) ]

    # Deletes the text file from our image array
    onlyfiles.pop(onlyfiles.index("info.txt"))

    # Basically I want to sort things with numbered prefixes and use them first
    # Then use the other images
    # I could use zip and such but I don't have the function handy that works well
    sec_list = [os.path.abspath(os.path.join(folder, x)) for x in onlyfiles if (x[1] != "_") or (x[0].isdigit() == False)]
    first_list = [os.path.abspath(os.path.join(folder, x)) for x in onlyfiles if (x[1] == "_") and (x[0].isdigit())]

    first_list.sort()
    sec_list.sort()

    allpics = []
    for x in first_list:allpics.append(x)
    for x in sec_list:allpics.append(x)

    # Opens the info file
    with open(os.path.abspath(os.path.join(folder, 'info.txt')), 'r') as info:

        # Parses the info file
        loc,title,types,cat,email,street,xstreet,state,postal,body,city,price = parse_text_file(info)
    
    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Go to craigslist postpage
    driver.get("https://post.craigslist.org/c/" + loc + "?lang=en")
    post_type(driver,types).click()
    post_category(driver,cat).click()
    try:
        abide_by_guidelines(driver).click() # Don't always have to do this for some reason
    except:
        pass
    create_post(driver,email=email,title=title,body=body,postal_code=postal,price=price)
    geo_location(driver,street=street,cross_street=xstreet,city=city,state=state,postal=postal)
    add_images(driver,allpics)

    moveFolder(folder,posted_dir)
