from scraper.autotrader_scraper import Autotrader_scraper
from scraper.timer import Timer

def test_result(is_pass):
    return "PASS" if is_pass else "FAIL"

def test_search_vehicle_type():
    with Timer():
        test_scraper = Autotrader_scraper()
        init_url = test_scraper.driver.current_url[:-1]
        test_scraper.search_vehicle_type("Lotus", "Elise")
        new_url = test_scraper.driver.current_url[:-1]
        test_scraper.close_session()
        is_pass = init_url != new_url
        print(f"Test case: test_search_vehicle_type() --> {test_result(is_pass)}")

def test_get_vehicle_list():
    pass


if __name__ == "__main__":
    test_search_vehicle_type()