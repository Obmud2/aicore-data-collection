import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from scraper.vehicle_data import Vehicle_data

class Autotrader_scraper:
    """
    Container class for the autotrader scraper tool.
    """
    def __init__(self, url="https://www.autotrader.co.uk", verbose=False):
        self.url = url
        self.verbose = verbose
        self.driver = webdriver.Safari()
        self.driver.implicitly_wait(0.5)
        self.driver.maximize_window()
        self.driver.get(self.url)
        if self.verbose: print(f"Navigated to {self.url}")
        self.__accept_cookies()

    def __accept_cookies(self):
        """
        Accept cookies on Autotrader homepage
        """
        delay = 10 # Max delay to wait for webpage load
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_687971"]')))
            self.driver.switch_to.frame("sp_message_iframe_687971")
            self.driver.find_element(by=By.XPATH, value="//button[@title='Accept All']").click()
            self.driver.switch_to.default_content()
            if self.verbose: print("Cookies accepted")
            time.sleep(1)
        except:
            print(f"Error accepting cookies")  
    
    def __parse_vehicle_list(self) -> list[Vehicle_data]:
        """
        Parse all useful data from search results list.

        Returns:
            list(Vehicle_data): Vehicle data from current search page.
        """
        vehicle_list = []
        vehicles = self.driver.find_elements(by=By.XPATH, value="//li[@class='search-page__result']")
        for vehicle in vehicles:
            if vehicle.get_attribute('data-is-promoted-listing')=="true":
                continue # Ignore promoted listings to avoid double vehicle entries
            else:
                vehicle_href = vehicle.find_element(by=By.XPATH, value="article/a").get_attribute('href')
                vehicle_id = re.findall('[0-9]{15}', vehicle_href)[0]
                vehicle_title = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__title").text.strip()
                vehicle_subtitle = vehicle.find_element(by=By.CLASS_NAME, value="product-card-details__subtitle").text.strip()
                vehicle_price = vehicle.find_element(by=By.CLASS_NAME, value="product-card-pricing__price").text.strip()
                vehicle_price = int(re.sub('[^0-9]', '', vehicle_price))
                vehicle_location = vehicle.find_elements(by=By.XPATH, value=".//span[@class='product-card-seller-info__spec-item-copy']")[-1].text

                vehicle_data = Vehicle_data(vehicle_id)
                vehicle_data.add_data(
                                href     = vehicle_href,
                                title    = vehicle_title,
                                subtitle = vehicle_subtitle,
                                price    = vehicle_price,
                                location = vehicle_location
                                )
                vehicle_list.append(vehicle_data)
        return vehicle_list
    
    def __parse_vehicle_page(self, vehicle_data) -> Vehicle_data:
        """
        Parses individual vehicle pages from a URL.
        Args:
            vehicle_data (Vehicle_data): Scraped data from individual vehicle. Vehicle data must include href(url). 
        Returns:
            Vehicle_data: Vehicle_data type including additional vehicle data scraped from vehicle page.
        """
        url = vehicle_data.get_url()
        self.driver.get(url)
        time.sleep(0.5)

        # Sets vehicle data to removed if ad expired
        if "expired-ad=true" in self.driver.current_url:
            vehicle_data.set_date_removed()
            return vehicle_data

        img_track = self.driver.find_element(by=By.XPATH, value="//div[@class='slick-track']")
        vehicle_img_list = []
        vehicle_img_list.append(img_track.find_element(by=By.XPATH, value=".//img").get_attribute("src"))

        vehicle_mileage = self.driver.find_element(by=By.XPATH, value="//span[@data-gui='mileage']").text.strip()
        vehicle_mileage = int(re.sub("[^0-9]", "", vehicle_mileage))

        try:
            desc_button = self.driver.find_element(by=By.XPATH, value="//button[@class='sc-hQYpqk sc-eQxmTn sc-ePZAhl cDuRCe kymA-DW kjRCRW atc-type-picanto atc-type-picanto--medium']")
            desc_button.click()
            vehicle_desc = self.driver.find_element(by=By.XPATH, value="//p[@class='sc-lcvaEy hePUbe atc-type-picanto']").text.strip()
            desc_exit_button = self.driver.find_element(by=By.XPATH, value="//button[@aria-label='Close']")
            desc_exit_button.click()
        except:
            # Use summary description if no 'Read more' button is present
            vehicle_desc = self.driver.find_element(by=By.XPATH, value="//p[@class='sc-iNhCjk jaeYBi atds-type-picanto']").text.strip()

        vehicle_data.add_data(
            mileage = vehicle_mileage,
            description = vehicle_desc,
            img = vehicle_img_list
        )

        return vehicle_data

    def search_vehicle_type(self, make_type="Lotus", model_type="Elise", postcode="BA229SZ"):
        """
        Searches for vehicle make and model from Autotrader homepage. Navigates driver to first search results page.
        Args:
            make_type (str): Make of vehicle from Autotrader list.
            model_type (str): Model of vehicle from Autotrader list.
            postcode (str): Postcode required to search Autotrader.
        """
        def __add_postcode(postcode):
            postcode_input = self.driver.find_element(by=By.XPATH, value="//input[@id='postcode']")
            postcode_input.click()
            postcode_input.send_keys(postcode)
            time.sleep(1)
        def __select_make(make):
            delay = 10 # Max delay to wait for model list to appear
            make_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='make']"))
            make_selection.select_by_value(make_type)
            WebDriverWait(self.driver, delay).until_not(EC.element_attribute_to_include((By.XPATH, "//select[@id='model']"), "disabled"))
            time.sleep(0.2)
        def __select_model(model):
            model_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='model']"))
            model_selection.select_by_value(model_type)
            time.sleep(1)
        def __click_search():
            search_button = self.driver.find_element(by=By.XPATH, value="//button[@data-gui='search-cars-button']")
            search_button.click()
            time.sleep(1)
            search_button.click() # Second click necessary to wait for page scrolling and page load.
            time.sleep(1)

        __add_postcode(postcode)
        __select_make(make_type)
        __select_model(model_type)
        __click_search()
        if self.verbose: print(f"Searching for {make_type} {model_type}")
    def get_vehicle_list(self, max_pages=0) -> list[Vehicle_data]:
        """
        Navigates through all search pages to create vehicle list of top level data, up to a max_page limit.
        By default all pages will be scraped.
        Args:
            max_pages (int): Maximum number of pages to scrape. Default=0 is all pages.
        Returns:
            list: Vehicle list in array of dictionaries.
        """
        search_url = self.driver.current_url[:-1]
        vehicle_list = []

        if max_pages == 0:
            pages_text = self.driver.find_element(by=By.XPATH, value="//li[@class='paginationMini__count']").text
            pages = int(pages_text.split()[-1])
        else:
            pages = max_pages

        for page in range(1, pages + 1):
            if self.verbose: print(f"Searching page {page} of {pages}")
            if page != 1:
                self.driver.get(f"{search_url}{page}")
            time.sleep(1)
            vehicle_list += self.__parse_vehicle_list()

        return vehicle_list   
    def add_vehicle_page_data(self, vehicle_list) -> list[Vehicle_data]:
        """
        Navigates to vehicle page and adds additional data not available on the search results pages.

        Args:
            vehicle_list (list[Vehicle_data]): List of scraped data for each vehicle in Vehicle_data class format.
        Returns:
            list: Updated vehicle list including new data from each vehicle page.
        """
        for vehicle_index in range(len(vehicle_list)):
            vehicle_list[vehicle_index] = self.__parse_vehicle_page(vehicle_list[vehicle_index])
        return vehicle_list

if __name__ == "__main__":
    scraper = Autotrader_scraper(verbose=True)
    scraper.search_vehicle_type("Lotus", "Elise")
    vehicle_data_list = scraper.get_vehicle_list(max_pages = 1)
    vehicle_data_list = scraper.add_vehicle_page_data(vehicle_data_list)
    scraper.driver.quit()

    for vehicle_data in vehicle_data_list:
        vehicle_data.save_data()
