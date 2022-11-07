# Main file for autotrader scraper project.

from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler
from tqdm import tqdm
import os, shutil

VEHICLE_MAKE = "Lotus"
VEHICLE_MODEL = 'Elise'
dir_name = f"{VEHICLE_MAKE.replace(' ','')}_{VEHICLE_MODEL.replace(' ','')}".lower()

scraper = Autotrader_scraper()
aws = AWS_handler()
vehicle_data_list = scraper.get_vehicle_list(VEHICLE_MAKE, VEHICLE_MODEL)
vehicle_data_list = scraper.get_vehicle_page_data(vehicle_data_list)
scraper.driver.quit()

Vehicle_data.save_list_to_local(vehicle_data_list, path='raw_data')
aws.upload_list_to_remote(vehicle_data_list, table=f"{VEHICLE_MAKE.lower()}_{VEHICLE_MODEL.lower()}")
aws.upload_to_s3(path='raw_data', folder_name=f"{VEHICLE_MAKE.lower()}_{VEHICLE_MODEL.lower()}")

dir = 'raw_data'
for files in os.listdir(dir):
    path = os.path.join(dir, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)
