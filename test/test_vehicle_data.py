import unittest
import os
from shutil import rmtree
from scraper.vehicle_data import Vehicle_data


class VehicleDataTestCase(unittest.TestCase):

    def test_save_to_local(self):
        """
        Check save data file structure matches with scraped data.
        """        
        vehicle_data_list = Vehicle_data.parse_json_vehicle_data_list("test/test_files/full_vehicle_data_list.json")
        test_dir_path = "test/raw_data"
        rmtree(test_dir_path, ignore_errors=True)
        vehicle_data_ids = []
        for vehicle_data in vehicle_data_list:
            vehicle_data.save_to_local(path=test_dir_path)
            vehicle_data_ids.append(vehicle_data.get_id())

        # Check all folders are created
        self.assertTrue(os.listdir(test_dir_path).sort() == vehicle_data_ids.sort(), "raw_data directory not complete")

        # Check of folder contents
        for vehicle_data in vehicle_data_list:
            vehicle_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}")
            self.assertTrue(vehicle_dir.sort() == ["data.json", "images"].sort(),'Saved data structure does not equal ["data.json", "images"]')           
            img_dir = os.listdir(f"{test_dir_path}/{vehicle_data.get_id()}/images")
            self.assertTrue(len(img_dir) == len(vehicle_data.get_data()['data']['img']), "Image files directory not complete")
