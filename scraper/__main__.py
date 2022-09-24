# Main file for autotrader scraper project.

from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data

scraper = Autotrader_scraper(verbose=True)
scraper.search_vehicle_type("Lotus", "Elise")
vehicle_data_list = scraper.get_vehicle_list(max_pages = 1)
vehicle_data_list = scraper.add_vehicle_page_data(vehicle_data_list)
scraper.driver.quit()
for vehicle_data in vehicle_data_list:
    vehicle_data.save_data()

df = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list)
print(df)
