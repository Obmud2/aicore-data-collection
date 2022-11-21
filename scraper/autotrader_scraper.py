import re
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm

from scraper.vehicle_data import Vehicle_data

class Autotrader_scraper:
    """
    Container class for the autotrader scraper tool.
    """
    def __init__(self, url="https://www.autotrader.co.uk", verbose=False, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  
            chrome_options.add_argument("window-size=1920,1080")
        self.url = url
        self.verbose = verbose
        self.driver = uc.Chrome(options=chrome_options, use_subprocess=True)
        self.driver.implicitly_wait(0.5)
        self.driver.maximize_window()
        self.driver.get(self.url)
        if self.verbose: print(f"Navigated to {self.url}")
        self.__accept_cookies()

    def __accept_cookies(self):
        """
        Accept cookies on Autotrader webpage
        """
        delay = 10 # Max delay to wait for webpage load
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_687971"]')))
            self.driver.switch_to.frame("sp_message_iframe_687971")
            self.driver.find_element(by=By.XPATH, value="//button[@title='Accept All']").click()
            self.driver.switch_to.default_content()
            if self.verbose: print("Cookies accepted")
            time.sleep(2)
        except Exception as e:
            print(e)
            print(f"Error accepting cookies")
    
    def __check_for_cookies_frame(self) -> bool:
        if self.driver.find_elements(by=By.XPATH, value='//iframe[@id="sp_message_iframe_687971"]'):
            return True
        else:
            return False

    def __parse_vehicle_list(self, vehicle_id_list) -> list[Vehicle_data]:
        """
        Parse all useful data from search results list.

        Returns:
            list(Vehicle_data): Vehicle data from current search page.
        """
        time.sleep(1)
        if self.__check_for_cookies_frame():
            self.__accept_cookies()
        
        vehicle_list = []
        vehicles = self.driver.find_elements(by=By.XPATH, value="//li[@class='search-page__result']")
        for vehicle in vehicles:
            vehicle_href = vehicle.find_element(by=By.XPATH, value="article/a").get_attribute('href')
            vehicle_id = re.findall('[0-9]{15}', vehicle_href)[0]
            if vehicle_id in vehicle_id_list:
                continue # Ignore promoted listings to avoid double vehicle entries
            else:
                vehicle_id_list.append(vehicle_id)
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
        if self.__check_for_cookies_frame():
            self.__accept_cookies()

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
            desc_button = self.driver.find_element(by=By.XPATH, value="//button[@class='sc-dksuTV sc-cOohKt sc-lMZDC zPuL ieYCDx nRsKQ atc-type-picanto atc-type-picanto--medium']")
            desc_button.click()
            time.sleep(1)
            vehicle_desc = self.driver.find_element(by=By.XPATH, value="//p[@class='sc-joaiRD gQkOux atc-type-picanto']").text.strip()
            desc_exit_button = self.driver.find_element(by=By.XPATH, value="//button[@aria-label='Close']")
            desc_exit_button.click()
        except:
            # Use summary description if no 'Read more' button is present
            vehicle_desc = self.driver.find_element(by=By.XPATH, value="//p[@class='sc-iLCGUA gVqxW atds-type-picanto']").text.strip()

        vehicle_data.add_data(
            mileage = vehicle_mileage,
            description = vehicle_desc,
            img = vehicle_img_list
        )

        return vehicle_data

    def __search_vehicle_type(self, make_type, model_type, postcode):
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
            time.sleep(2)
        def __select_make(make):
            delay = 10 # Max delay to wait for model list to appear
            while (next((attr['name'] for attr in self.driver.find_element(By.XPATH, "//select[@id='model']").get_property('attributes') if attr['name']=='disabled'), False)):
                make_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='make']"))
                make_selection.select_by_value(make)
                time.sleep(2)
            time.sleep(2)
        def __select_model(model):
            model_selection = Select(self.driver.find_element(by=By.XPATH, value="//select[@id='model']"))
            model_selection.select_by_value(model)
            time.sleep(2)
        def __click_search():
            search_button = self.driver.find_element(by=By.XPATH, value="//button[@data-gui='search-cars-button']")
            search_button.click()
            time.sleep(2)

        __add_postcode(postcode)
        __select_make(make_type)
        __select_model(model_type)
        __click_search()
    
    def get_vehicle_list(self, make_type, model_type, postcode="FK78BH", max_pages=0) -> list[Vehicle_data]:
        """
        Navigates through all search pages to create vehicle list of top level data, up to a max_page limit.
        By default all pages will be scraped.
        Args:
            max_pages (int): Maximum number of pages to scrape. Default=0 is all pages.
        Returns:
            list: Vehicle list in array of dictionaries.
        """
        for i in tqdm(range(1), desc=f"Searching for {make_type} {model_type}...: "):
            self.__search_vehicle_type(make_type, model_type, postcode)
        
        search_url = self.driver.current_url[:-1]
        vehicle_list = []
        vehicle_id_list = []

        if max_pages == 0:
            pages_text = self.driver.find_element(by=By.XPATH, value="//li[@class='paginationMini__count']").text
            pages = int(pages_text.split()[-1])
        else:
            pages = max_pages

        for page in tqdm(range(1, pages + 1), desc="Scraping search results...: "):
            if page != 1:
                search_url_page = re.sub(r'page=1?', f'page={page}', search_url)
                self.driver.get(search_url_page)
            time.sleep(1)
            vehicle_list += self.__parse_vehicle_list(vehicle_id_list)

        return vehicle_list   
    
    def get_vehicle_page_data(self, vehicle_list) -> list[Vehicle_data]:
        """
        Navigates to vehicle page and adds additional data not available on the search results pages.

        Args:
            vehicle_list (list[Vehicle_data]): List of scraped data for each vehicle in Vehicle_data class format.
        Returns:
            list: Updated vehicle list including new data from each vehicle page.
        """
        for vehicle_index in tqdm(range(len(vehicle_list)), desc="Scraping vehicle pages...: "):
            vehicle_list[vehicle_index] = self.__parse_vehicle_page(vehicle_list[vehicle_index])
        return vehicle_list

if __name__ == "__main__":
    pass
