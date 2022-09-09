from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import re
from random import uniform
from uuid import uuid4

class Autotrader_scraper:
    def __init__(self):
        self.url = "https://www.autotrader.co.uk"
        self.delay = 10

        self.driver = webdriver.Safari()
        self.driver.implicitly_wait(0.5)
        self.driver.maximize_window()
        self.driver.get(self.url)
        print(f"Navigated to {self.url}")

    def __sleep(self, duration = 1, distribution=0.2):
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
            self.__sleep(1)
        except:
            print(f"Error accepting cookies")  
    def search_vehicle_type(self, make_type="Lotus", model_type="Elise", postcode="BA229SZ"):

        postcode_input = self.driver.find_element(by=By.XPATH, value="//input[@id='postcode']")
        postcode_input.click()
        postcode_input.send_keys(postcode)
        self.__sleep(1)

        make_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='make']"))
        make_selection.select_by_value(make_type)
        WebDriverWait(self.driver, self.delay).until_not(EC.element_attribute_to_include((By.XPATH, "//select[@id='model']"), "disabled"))
        model_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='model']"))
        model_selection.select_by_value(model_type)
        self.__sleep(1)

        
        search_button = self.driver.find_element(by=By.XPATH, value="//button[@data-gui='search-cars-button']")
        print(f"Clicking button \"{search_button.text}\"")
        search_button.click()
        self.__sleep(1)
        search_button.click()
        self.__sleep(1)

        print(f"Searching for {make_type} {model_type}")
    def get_url_list(self, max_pages=0):
        vehicle_list = []
        search_url = self.driver.current_url[:-1]

        if max_pages == 0:
            pages_text = self.driver.find_element(by=By.XPATH, value="//li[@class='paginationMini__count']").text
            pages = int(pages_text.split()[-1])
        else:
            pages = max_pages

        for page in range(1, pages + 1):
            print(f"Searching page {page} of {pages}")
            if page != 1:
                self.driver.get(f"{search_url}{page}")
            self.__sleep(1)

            vehicles = self.driver.find_elements(by=By.XPATH, value="//li[@class='search-page__result']")

            for vehicle in vehicles:
                vehicle_standout = vehicle.find_elements(by=By.XPATH, value="span")
                if vehicle_standout and vehicle_standout[0].text == 'Ad':
                    continue
                else:
                    vehicle_href = vehicle.find_element(by=By.XPATH, value="article/a").get_attribute('href')
                    vehicle_id = re.findall('[0-9]{15}', vehicle_href)[0]
                    vehicle_title = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__title").text.strip()
                    vehicle_subtitle = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__subtitle").text.strip()
                    vehicle_price = vehicle.find_element(by=By.CLASS_NAME, value="product-card-pricing__price").text.strip()
                    vehicle_location = vehicle.find_elements(by=By.XPATH, value=".//span[@class='product-card-seller-info__spec-item-copy']")[-1].text
                    
                    vehicle_list.append([vehicle_id, uuid4(), vehicle_href, vehicle_title, vehicle_subtitle, vehicle_price, vehicle_location])

            print(f"{len(vehicles)} vehicles found on page {page}.")

        return vehicle_list

    def parse_vehicle_page(self, vehicle_url):
        self.driver.get(vehicle_url)
        self.__sleep(1)

        img_track = self.driver.find_element(by=By.XPATH, value="//div[@class='slick-track']")
        vehicle_img = img_track.find_element(by=By.XPATH, value=".//img").get_attribute("src")

        vehicle_mileage = self.driver.find_element(by=By.XPATH, value="//span[@data-gui='mileage']").text.strip()

        desc_button = self.driver.find_element(by=By.XPATH, value="//button[@class='sc-hQYpqk sc-feWZte sc-iyHPJt cDuRCe eFGeSa gexRyG atc-type-picanto atc-type-picanto--medium']")
        desc_button.click()
        vehicle_desc = self.driver.find_element(by=By.XPATH, value="//p[@class='sc-ffgBur byDqpY atc-type-picanto']").text.strip()
        self.__sleep(0.2, 0)
        desc_exit_button = self.driver.find_element(by=By.XPATH, value="//button[@aria-label='Close']")
        desc_exit_button.click()

        vehicle_data=[vehicle_mileage, vehicle_desc, vehicle_img]

        return vehicle_data
    def add_vehicle_page_data(self, vehicle_list):
        new_vehicle_list = []
        for vehicle in vehicle_list:
            data = self.parse_vehicle_page(vehicle[2])
            new_vehicle_list.append(vehicle + data)
        return new_vehicle_list


    def close(self):
        self.driver.close()



if __name__ == "__main__":
    test = Autotrader_scraper()
    test.accept_cookies()
    test.search_vehicle_type("Lotus", "Exige")
    results = test.get_url_list()
    test.close()