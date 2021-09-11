import os
import time
from selenium import webdriver

URL = os.environ.get("PULSOID_URL")


class Scraper:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.set_window_size(100, 200)
        self.browser.get(URL)

    def get_rate(self):
        try:
            hr = browser.find_element_by_id("heartRate")
            string = hr.get_attribute("innerHTML")
            string = string[string.rfind(">") + 1 :]
            return int(string)
        except:
            pass
        return None
