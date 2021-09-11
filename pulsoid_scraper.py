import os
import time
from selenium import webdriver
URL = os.environ.get("PULSOID_URL")
browser = webdriver.Chrome()
browser.set_window_size(100, 200)

browser.get(URL)
elem = browser.find_element_by_xpath("//*")
source_code = elem.get_attribute("outerHTML")

for i in range (20):
    time.sleep(1)    
    source = browser.page_source
    try:
        hr = browser.find_element_by_id("heartRate")        
        string = hr.get_attribute('innerHTML')
        string = string[string.rfind(">")+1:]
        print(string)        
    except:
        continue    
        



