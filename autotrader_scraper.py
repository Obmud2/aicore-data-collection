#from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys

import time
from random import uniform

class Autotrader_scraper:
    def __init__(self):
        self.url = "https://www.autotrader.co.uk"
        self.delay = 10
        
        self.driver = webdriver.Safari()
        self.driver.get(self.url)
        print(f"Navigated to {self.url}")

    def __sleep(self, duration = 2, distribution=0.5):
        time.sleep(duration + uniform(-distribution, distribution))

    def accept_cookies(self):
        """
        Accept cookies on Autotrader homepage
        """
        try:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_687971"]')))
            self.driver.switch_to.frame("sp_message_iframe_687971")
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//button[@title='Accept All']")
            accept_cookies_button.click()
            self.driver.switch_to.default_content()
            print("Cookies accepted")
        except:
            print(f"Error accepting cookies")
    
    def search_vehicle_type(self, make_type="Lotus", model_type="Elise", postcode="BA229SZ"):
        postcode_input = self.driver.find_element(by=By.XPATH, value="//input[@id='postcode']")
        postcode_input.click()
        postcode_input.send_keys(postcode)

        make_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='make']"))
        make_selection.select_by_value(make_type)
        WebDriverWait(self.driver, self.delay).until_not(EC.element_attribute_to_include((By.XPATH, "//select[@id='model']"), "disabled"))
        model_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='model']"))
        model_selection.select_by_value(model_type)
        print(f"{make_type} {model_type} selected")

        search_button = self.driver.find_element(by=By.XPATH, value="//button[@type='submit']")
        search_button.click()
        self.__sleep(1)

    def get_url_list(self):
        pass

    def get_vehicle_data(self, vehicle_url):
        pass

    def close(self):
        self.driver.close()



if __name__ == "__main__":
    test = Autotrader_scraper()
    test.accept_cookies()
    test.search_vehicle_type("BMW", "4 Series Gran Coupe")
    
    time.sleep(5)
    test.close()