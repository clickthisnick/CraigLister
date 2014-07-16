from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time
import os

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
    import shutil
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
    body =  ''.join([i if ord(i) < 128 else '' for i in body])

    # tabs will actually go to the next field in craiglist
    body = "     ".join(body.split("\t"))
    
    price = parsing(f,"<Price>")
    return loc.lower(),title,types,cat,email,street,xstreet,state,postal,body,city,price

posts_dir = os.path.abspath(os.path.join(os.getcwd(), "posts"))
posted_dir = os.path.join(posts_dir,"posted")

# Make the posted folder
makeFolder(posted_dir)

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
                          
