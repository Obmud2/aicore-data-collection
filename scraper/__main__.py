# Main file for autotrader scraper project.

from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler
from tqdm import tqdm

VEHICLE_MAKE = "Lotus"
VEHICLE_MODEL = 'Elise'
dir_name = f"{VEHICLE_MAKE.replace(' ','')}_{VEHICLE_MODEL.replace(' ','')}".lower()

scraper = Autotrader_scraper()
scraper.search_vehicle_type(VEHICLE_MAKE, VEHICLE_MODEL)
vehicle_data_list = scraper.get_vehicle_list(max_pages = 2)
vehicle_data_list = scraper.get_vehicle_page_data(vehicle_data_list)
scraper.driver.quit()

print(Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list))

storage_method = Vehicle_data.select_storage_method()
if "local" in storage_method:
    for vehicle_data in tqdm(vehicle_data_list, desc="Saving data to local..."):
        vehicle_data.save_to_local()
if "rds" in storage_method:
    AWS_handler.upload_to_rds(vehicle_data_list, table=dir_name)
    AWS_handler.upload_to_s3(path='raw_data', search_name=dir_name)
