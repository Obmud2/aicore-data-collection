from scraper.autotrader_scraper import Autotrader_scraper
from scraper.timer import Timer
import unittest
from bs4 import BeautifulSoup
from shutil import rmtree
import os
import urllib.request
import re
import json

from scraper.vehicle_data import Vehicle_data

# def print_test_result(is_pass, test_case_name):
#     print(f"Test case: {test_case_name} --> {'PASS' if is_pass else 'FAIL'}")

# def test_save_data(vehicle_data_list = None):
#     """
#     Check save data file structure matches with scraped data.
#     """
#     with Timer():
#         if vehicle_data_list == None:
#             test_search_results_url = "https://www.autotrader.co.uk/car-search?postcode=ba229sz&make=Lotus&model=Exige&include-delivery-option=on&advertising-location=at_cars&page=1"
#             test_scraper = Autotrader_scraper(test_search_results_url)
#             vehicle_data_list = test_scraper.get_vehicle_list(max_pages=1)
#             vehicle_data_list = test_scraper.add_vehicle_page_data(vehicle_data_list)

#         test_dir_path = "test/raw_data"
#         is_pass = True
#         rmtree(test_dir_path, ignore_errors=True)
#         vehicle_data_ids = []
#         for vehicle_data in vehicle_data_list:
#             vehicle_data.save_data(path=test_dir_path)
#             vehicle_data_ids.append(vehicle_data.get_id())

#         # Check all folders are created
#         if os.listdir(test_dir_path).sort() != vehicle_data_ids.sort():
#             is_pass = False

#         # Check of folder contents
#         for vehicle_data in vehicle_data_list:
#             vehicle_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}")
#             if vehicle_dir.sort() != ["data.json", "images"].sort():
#                 is_pass = False
#             img_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}/images")
#             if len(img_dir) != len(vehicle_data.get_data()['data']['img']):
#                 is_pass = False

#         print_test_result(is_pass, "test_save_data()")

class ScraperTestCase(unittest.TestCase):
    
    def setUp(self):
        self.test_scraper = Autotrader_scraper()
        self.vehicle_data_list = []
        self.test_make = "Lotus"
        self.test_model = "Exige"
    
    def test_search_vehicle_type(self):
        """
        Check that search is completed and new url is reached including search terms
        """

        init_url = self.test_scraper.driver.current_url[:-1]
        self.test_scraper.search_vehicle_type(self.test_make, self.test_model)
        new_url = self.test_scraper.driver.current_url[:-1]
        self.assertTrue(init_url != new_url and self.test_make in new_url and self.test_model in new_url)

    def test_get_vehicle_list(self):
        """
        Check that number of listed vehicles matches number of results scraped.
        """
        test_search_results_url = "https://www.autotrader.co.uk/car-search?postcode=ba229sz&make=Lotus&model=Exige&include-delivery-option=on&advertising-location=at_cars&page=1"
        self.test_scraper.driver.get(test_search_results_url)
        
        def scrape_num_results(test_search_results_url):
            page = urllib.request.urlopen(test_search_results_url)
            soup = BeautifulSoup(page, 'html.parser')
            num_results = soup.find('h1', class_='search-form__count js-results-count').get_text()
            return int(re.sub("[^0-9]",'',num_results))
        
        self.vehicle_data_list = self.test_scraper.get_vehicle_list()
        self.assertTrue(len(self.vehicle_data_list) == scrape_num_results(test_search_results_url))

    def test_add_vehicle_page_data(self):
        """
        Check for all data added to Vehicle_data is non-empty for sample of pages.
        """
        num_samples = min([3,len(self.vehicle_data_list)])
        self.vehicle_data_list = self.test_scraper.add_vehicle_page_data(self.vehicle_data_list[:num_samples])
        is_pass = True
        for vehicle in self.vehicle_data_list:
            vehicle_data = vehicle.get_data()
            if vehicle_data["id"] == None or vehicle_data["uuid"] == None:
                is_pass = False
            for data in vehicle_data["data"].values():
                if data == None:
                    is_pass = False
        self.assertTrue(is_pass)

    def test_save_data(self):
        """
        Check save data file structure matches with scraped data.
        """
        def import_vehicle_data_list():
            with open("test/test_files/full_vehicle_data_list.json", 'r') as of:
                vehicle_data_list_from_json = json.load(of)
            vehicle_data_list = []
            for vehicle in vehicle_data_list_from_json:
                vehicle_data = Vehicle_data(vehicle['id'], vehicle['uuid'])
                vehicle_data.add_data(**vehicle['data'])
                vehicle_data_list.append(vehicle_data)
            return vehicle_data_list
        
        self.vehicle_data_list = import_vehicle_data_list()
        test_dir_path = "test/raw_data"
        rmtree(test_dir_path, ignore_errors=True)
        vehicle_data_ids = []
        for vehicle_data in self.vehicle_data_list:
            vehicle_data.save_data(path=test_dir_path)
            vehicle_data_ids.append(vehicle_data.get_id())

        # Check all folders are created
        self.assertTrue(os.listdir(test_dir_path).sort() == vehicle_data_ids.sort(), "raw_data directory not complete")

        # Check of folder contents
        for vehicle_data in self.vehicle_data_list:
            vehicle_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}")
            self.assertTrue(vehicle_dir.sort() == ["data.json", "images"].sort(),'Saved data structure does not equal ["data.json", "images"]')           
            img_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}/images")
            self.assertTrue(len(img_dir) == len(vehicle_data.get_data()['data']['img']), "Image files directory not complete")

    def tearDown(self):
        self.test_scraper.close_session()


if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)