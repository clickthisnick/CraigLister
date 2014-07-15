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
    price = parsing(f,"<Price>")
    return loc.lower(),title,types,cat,email,street,xstreet,state,postal,body,city,price

posts_dir = os.path.abspath(os.path.join(os.getcwd(), "posts"))

folders = [os.path.abspath(os.path.join(posts_dir, child)) for child in os.listdir(posts_dir)]
for folder in folders:
    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) ]
    onlyfiles.pop(onlyfiles.index("info.txt"))

    first_list = []
    sec_list = []
    for x in onlyfiles:
        if (x[1] != "_") or (x[0].isdigit() == False):sec_list.append(os.path.abspath(os.path.join(folder, x)))
        else:first_list.append(os.path.abspath(os.path.join(folder, x)))

    first_list.sort()
    sec_list.sort()

    allpics = []
    for x in first_list:allpics.append(x)
    for x in sec_list:allpics.append(x)
    
    info = open(os.path.abspath(os.path.join(folder, 'info.txt')), 'r')
    loc,title,types,cat,email,street,xstreet,state,postal,body,city,price = parse_text_file(info)
    
    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Go to craigslist postpage
    driver.get("https://post.craigslist.org/c/" + loc + "?lang=en")
    post_type(driver,types).click()
    post_category(driver,cat).click()
    try:
        abide_by_guidelines(driver).click()
    except:
        pass
    create_post(driver,email=email,title=title,body=body,postal_code=postal,price=price)
    geo_location(driver,street=street,cross_street=xstreet,city=city,state=state,postal=postal)
    add_images(driver,allpics)
