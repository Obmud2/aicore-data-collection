from scraper.autotrader_scraper import Autotrader_scraper
from scraper.timer import Timer
from bs4 import BeautifulSoup
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

if __name__ == "__main__":
    test_search_vehicle_type()
    test_get_vehicle_list()