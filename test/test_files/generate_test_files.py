
import json
from scraper.autotrader_scraper import Autotrader_scraper
from scraper.vehicle_data import Vehicle_data

if __name__ == "__main__":
    scraper = Autotrader_scraper()
    scraper.search_vehicle_type("Lotus", "Exige")
    vehicle_data_list = scraper.get_vehicle_list(max_pages = 1)
    vehicle_data_list_json = []
    for vehicle in vehicle_data_list:
        vehicle_data_list_json.append(vehicle.get_data())

    json_object = json.dumps(vehicle_data_list_json, indent=4, default=str)
    with open(f"test/test_files/initial_vehicle_data_list.json", 'w') as of:
        of.write(json_object)

    vehicle_data_list = scraper.get_vehicle_page_data(vehicle_data_list[:3])
    vehicle_data_list_json = []
    for vehicle in vehicle_data_list:
        vehicle_data_list_json.append(vehicle.get_data())

    json_object = json.dumps(vehicle_data_list_json, indent=4, default=str)
    with open(f"test/test_files/full_vehicle_data_list.json", 'w') as of:
        of.write(json_object)

    Vehicle_data.save_list_to_local(vehicle_data_list, path='test/test_files/raw_data')

    scraper.driver.quit()