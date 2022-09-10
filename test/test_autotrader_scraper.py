from scraper.autotrader_scraper import Autotrader_scraper
from scraper.timer import Timer
from bs4 import BeautifulSoup
from shutil import rmtree
import os
import urllib.request
import re

def print_test_result(is_pass, test_case_name):
    print(f"Test case: {test_case_name} --> {'PASS' if is_pass else 'FAIL'}")

def test_search_vehicle_type():
    """
    Check that search is completed and new url is reached including search terms
    """
    with Timer():
        test_make = "Lotus"
        test_model = "Exige"
        test_scraper = Autotrader_scraper()
        init_url = test_scraper.driver.current_url[:-1]
        test_scraper.search_vehicle_type(test_make, test_model)
        new_url = test_scraper.driver.current_url[:-1]
        test_scraper.close_session()
        is_pass = init_url != new_url and test_make in new_url and test_model in new_url
        print_test_result(is_pass, "test_search_vehicle_type()")
def test_get_vehicle_list():
    """
    Check that number of listed vehicles matches number of results scraped.
    """
    def scrape_num_results(test_search_results_url):
        page = urllib.request.urlopen(test_search_results_url)
        soup = BeautifulSoup(page, 'html.parser')
        num_results = soup.find('h1', class_='search-form__count js-results-count').get_text()
        return int(re.sub("[^0-9]",'',num_results))
    test_search_results_url = "https://www.autotrader.co.uk/car-search?postcode=ba229sz&make=Lotus&model=Exige&include-delivery-option=on&advertising-location=at_cars&page=1"
    with Timer():
        test_scraper = Autotrader_scraper(test_search_results_url)
        vehicle_data_list = test_scraper.get_vehicle_list()
        test_scraper.close_session()
        is_pass = len(vehicle_data_list) == scrape_num_results(test_search_results_url)
        print_test_result(is_pass, "test_get_vehicle_list()")
    return vehicle_data_list
def test_add_vehicle_page_data(vehicle_data_list = None):
    """
    Check for all data added to Vehicle_data for sample of pages.
    """
    test_search_results_url = "https://www.autotrader.co.uk/car-search?postcode=ba229sz&make=Lotus&model=Exige&include-delivery-option=on&advertising-location=at_cars&page=1"
    with Timer():
        if vehicle_data_list == None:
            test_scraper = Autotrader_scraper(test_search_results_url)
            vehicle_data_list = test_scraper.get_vehicle_list(max_pages=1)
        else:
            test_scraper = Autotrader_scraper(vehicle_data_list[0].get_url())
        
        num_tests = min([3,len(vehicle_data_list)])
        vehicle_data_list_sample = test_scraper.add_vehicle_page_data(vehicle_data_list[:num_tests])
        test_scraper.close_session()
        is_pass = True
        for vehicle in vehicle_data_list_sample:
            vehicle_data = vehicle.get_data()
            if vehicle_data["id"] == None or vehicle_data["uuid"] == None:
                is_pass = False
            for data in vehicle_data["data"].values():
                if data == None:
                    is_pass = False
        print_test_result(is_pass, "test_add_vehicle_page_data()")
    return vehicle_data_list_sample
def test_save_data(vehicle_data_list = None):
    with Timer():
        if vehicle_data_list == None:
            test_search_results_url = "https://www.autotrader.co.uk/car-search?postcode=ba229sz&make=Lotus&model=Exige&include-delivery-option=on&advertising-location=at_cars&page=1"
            test_scraper = Autotrader_scraper(test_search_results_url)
            vehicle_data_list = test_scraper.get_vehicle_list(max_pages=1)
            vehicle_data_list = test_scraper.add_vehicle_page_data(vehicle_data_list)

        test_dir_path = "test/raw_data"
        is_pass = True
        rmtree(test_dir_path, ignore_errors=True)
        vehicle_data_ids = []
        for vehicle_data in vehicle_data_list:
            vehicle_data.save_data(path=test_dir_path)
            vehicle_data_ids.append(vehicle_data.get_id())

        # Check all folders are created
        if os.listdir(test_dir_path).sort() != vehicle_data_ids.sort():
            is_pass = False

        # Check of folder contents
        for vehicle_data in vehicle_data_list:
            vehicle_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}")
            if vehicle_dir.sort() != ["data.json", "images"].sort():
                is_pass = False
            img_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}/images")
            if len(img_dir) != len(vehicle_data.get_data()['data']['img']):
                is_pass = False

        print_test_result(is_pass, "test_save_data()")

if __name__ == "__main__":
    test_search_vehicle_type()
    vehicle_data_list = test_get_vehicle_list()
    vehicle_data_list = test_add_vehicle_page_data(vehicle_data_list)
    test_save_data(vehicle_data_list)