from scraper.autotrader_scraper import Autotrader_scraper
import unittest
from bs4 import BeautifulSoup
import urllib.request
import re

from scraper.vehicle_data import Vehicle_data

class ScraperTestCase(unittest.TestCase):
    
    def setUp(self):
        self.vehicle_data_list = []
        self.test_make = "Lotus"
        self.test_model = "Exige"
    
    # def test_search_vehicle_type(self):
    #     """
    #     Check that search is completed and new url is reached including search terms
    #     """
    #     self.test_scraper = Autotrader_scraper()
    #     init_url = self.test_scraper.driver.current_url[:-1]
    #     self.test_scraper.search_vehicle_type(self.test_make, self.test_model)
    #     new_url = self.test_scraper.driver.current_url[:-1]
    #     self.assertTrue(init_url != new_url and self.test_make in new_url and self.test_model in new_url)

    def test_get_vehicle_list(self):
        """
        Check that number of listed vehicles matches number of results scraped.
        """
        self.test_scraper = Autotrader_scraper()
        
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
        self.test_scraper = Autotrader_scraper()
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