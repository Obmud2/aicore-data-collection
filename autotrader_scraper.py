from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
from random import uniform
from tabulate import tabulate

class Autotrader_scraper:
    def __init__(self):
        self.url = "https://www.autotrader.co.uk"
        self.delay = 10

        self.driver = webdriver.Safari()
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
        search_button.click()
        search_button.click()
        self.__sleep(2)

        print(f"Searching for {make_type} {model_type}")

    def get_url_list(self, pages=0):
        results_list = []
        search_url = self.driver.current_url[:-1]

        if pages == 0:
            pages_text = self.driver.find_element(by=By.XPATH, value="//li[@class='paginationMini__count']").text
            pages = int(pages_text.split()[-1])

        for page in range(1, pages + 1):
            print(f"Searching page {page} of {pages}")
            if page != 1:
                self.driver.get(f"{search_url}{page}")
            self.__sleep(1)

            vehicles = self.driver.find_elements(by=By.XPATH, value="//li[@class='search-page__result']")

            for vehicle in vehicles:
                vehicle_standout = vehicle.find_elements(by=By.XPATH, value="span")
                
                print(vehicle_standout[0].text) if vehicle_standout else print("not ad")
                if vehicle_standout and vehicle_standout[0].text == 'Ad':
                    continue
                else:
                    vehicle_href = vehicle.find_element(by=By.XPATH, value="article/a").get_attribute('href')
                    vehicle_title = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__title").text
                    vehicle_subtitle = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__subtitle").text
                    vehicle_price = vehicle.find_element(by=By.CLASS_NAME, value="product-card-pricing__price").text.strip()
                    results_list.append([vehicle_href, vehicle_title, vehicle_subtitle, vehicle_price])

            print(f"{len(vehicles)} vehicles found on page {page}.")

        return results_list


    def get_vehicle_data(self, vehicle_url):
        pass

    def close(self):
        self.driver.close()



if __name__ == "__main__":
    test = Autotrader_scraper()
    test.accept_cookies()
    test.search_vehicle_type("Lotus", "Exige")
    results = test.get_url_list(0)

    results.sort(key=lambda x:x[3])

    print(tabulate(results, headers=['url', 'title', 'subtitle', 'price'], maxcolwidths=[20, 20, 20, None]))
    
    print(f"number of results {len(results)}")

    time.sleep(5)
    test.close()