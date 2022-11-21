import unittest
import urllib.request
import re
from bs4 import BeautifulSoup

from scraper.vehicle_data import Vehicle_data
from scraper.autotrader_scraper import Autotrader_scraper

class ScraperTestCase(unittest.TestCase):
    
    def setUp(self):
        self.vehicle_data_list = []
        self.test_make = "Lotus"
        self.test_model = "Exige"

    def test_get_vehicle_list(self):
        """
        Check that number of listed vehicles matches number of results scraped.
        """
        self.test_scraper = Autotrader_scraper(headless=False)
        
        def scrape_num_results(test_search_results_url):
            page = urllib.request.urlopen(test_search_results_url)
            soup = BeautifulSoup(page, 'html.parser')
            num_results = soup.find('h1', class_='search-form__count js-results-count').get_text()
            return int(re.sub("[^0-9]",'',num_results))
        
        vehicle_data_list = self.test_scraper.get_vehicle_list('Lotus', 'Elise')
        self.assertTrue(len(vehicle_data_list) == scrape_num_results(self.test_scraper.driver.current_url))

    def test_get_vehicle_page_data(self):
        """
        Check for all data added to Vehicle_data is non-empty for sample of pages.
        """
        self.vehicle_data_list = Vehicle_data.parse_json_vehicle_data_list("test/test_files/initial_vehicle_data_list.json")
        self.test_scraper = Autotrader_scraper(headless=False)
        num_samples = min([100,len(self.vehicle_data_list)])
        self.vehicle_data_list = self.test_scraper.get_vehicle_page_data(self.vehicle_data_list[:num_samples])
        for vehicle in self.vehicle_data_list:
            vehicle_data = vehicle.get_data()
            self.assertTrue(vehicle_data["id"] and vehicle_data["uuid"])
            if not vehicle_data["date_removed"]:
                for data in vehicle_data["data"].values():
                    self.assertTrue(data, msg=f"failed on url {vehicle_data['data']}")

    def tearDown(self):
        self.test_scraper.driver.quit()


if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)