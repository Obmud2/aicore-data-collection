# Main file for autotrader scraper project.

from autotrader_scraper import Autotrader_scraper

scraper = Autotrader_scraper()
scraper.search_vehicle_type("Lotus", "Elise")
vehicle_data_list = scraper.get_vehicle_list(max_pages = 1)
vehicle_data_list = scraper.add_vehicle_page_data(vehicle_data_list)
scraper.close_session()
scraper.save_data(vehicle_data_list)