# Main file for autotrader scraper project.
import sys, datetime
from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler

try:
    VEHICLE_MAKE = sys.argv[1]
    VEHICLE_MODEL = sys.argv[2]
except:
    print("Input error")
    VEHICLE_MAKE = "Lotus"
    VEHICLE_MODEL = 'Elise'
print(f"{datetime.datetime.now()}: Searching for {VEHICLE_MAKE} {VEHICLE_MODEL}")

dir_name = f"{VEHICLE_MAKE.replace(' ','')}_{VEHICLE_MODEL.replace(' ','')}".lower()

scraper = Autotrader_scraper(headless=True)
aws = AWS_handler()
vehicle_data_list = scraper.get_vehicle_list(VEHICLE_MAKE, VEHICLE_MODEL, max_pages=0)
print(f"{datetime.datetime.now()}: {len(vehicle_data_list)} results found")
vehicle_data_list = scraper.get_vehicle_page_data(vehicle_data_list)
for v in vehicle_data_list:
    print(f"{v.get_data(flattened=True)['date_scraped']}: {v.get_data(flattened=True)['id']}")
scraper.driver.quit()

Vehicle_data.save_list_to_local(vehicle_data_list, path='raw_data')
aws.upload_list_to_remote(vehicle_data_list, table=f"{VEHICLE_MAKE.lower()}_{VEHICLE_MODEL.lower()}", verbose=True)
aws.upload_to_s3(path='raw_data', folder_name=f"{VEHICLE_MAKE.lower()}_{VEHICLE_MODEL.lower()}", verbose=True)
Vehicle_data.rm_local_dir('raw_data')
