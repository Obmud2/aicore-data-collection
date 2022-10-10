# Main file for autotrader scraper project.

from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler

VEHICLE_MAKE = "Lotus"
VEHICLE_MODEL = 'Elise'
dir_name = f"{VEHICLE_MAKE.replace(' ','')}_{VEHICLE_MODEL.replace(' ','')}".lower()

scraper = Autotrader_scraper()
scraper.search_vehicle_type(VEHICLE_MAKE, VEHICLE_MODEL)
vehicle_data_list = scraper.get_vehicle_list(max_pages = 1)
vehicle_data_list = scraper.get_vehicle_page_data(vehicle_data_list)
scraper.driver.quit()
for vehicle_data in vehicle_data_list:
    vehicle_data.save_data()

df = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list)

AWS_handler.upload_to_rds(df, table=dir_name)
AWS_handler.upload_to_s3(path='raw_data', search_name=dir_name)
