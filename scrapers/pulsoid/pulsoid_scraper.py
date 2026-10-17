import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller


URL = os.environ.get("PULSOID_URL")
chromedriver_autoinstaller.install()


class Scraper:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.set_window_size(100, 200)
        self.browser.get(URL)

    def get_rate(self):
        try:
            hr = self.browser.find_element(By.ID, "heartRate")
            return int(hr.text)
        except:
            pass
        return 0
