from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from random import uniform

class Scraper:
    def __init__(self):
        self.url = "https://www.autotrader.co.uk"
        self.driver = webdriver.Safari()
        self.driver.get(self.url)
        self.__sleep(2)

    def __sleep(self, duration = 2):
        time.sleep(duration + uniform(-0.5, 0.5))

    def accept_cookies(self):
        """
        Accept cookies on Autotrader homepage
        """
        try:
            self.driver.switch_to.frame("sp_message_iframe_687971")
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//button[@title='Accept All']")
            accept_cookies_button.click()
            print("Cookies accepted")
            self.__sleep(1)
        except:
            print(f"Error accepting cookies")
    
    def search_vehicle_type_advanced():
        pass

    def get_url_list():
        pass

    def get_vehicle_data():
        pass

    def close(self):
        self.driver.close()



if __name__ == "__main__":
    test = Scraper()
    test.accept_cookies()
    
    time.sleep(5)
    test.close()