from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time

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
    driver.find_element_by_xpath("//*[@id='leafletForm']/button[1]").click()
    print "hi"
    return
    #driver.find_element_by_id("xstreet0").send_keys(street)
    #driver.find_element_by_id("xstreet1").send_keys(cross_street)
    #driver.find_element_by_id("city").send_keys(city)
    #driver.find_element_by_id("region").send_keys(state)
    #driver.find_element_by_id("postal_code").send_keys(postal)
    
def add_images(driver):
    driver.find_element_by_id("plupload").click()
    driver.find_element_by_xpath("//*[@id='pagecontainer']/section/form/button").click()

    
# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# Go to craigslist postpage
driver.get("https://post.craigslist.org/c/ame?lang=en")
post_type(driver,"for sale by dealer").click()
post_category(driver,"furniture - by dealer").click()
try:
    abide_by_guidelines(driver).click()
except:
    pass
create_post(driver,email="a@enterthebunker.com",title="Furniture Surplus",body="For good furniture",postal_code=50010,price="")
geo_location(driver,street="",cross_street="",city="",state="",postal="")

import win32com.client
shell = win32com.client.Dispatch("WScript.Shell")
shell.SendKeys("{ENTER}", 0)

