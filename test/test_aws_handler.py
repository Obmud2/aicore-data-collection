import unittest
import os
import pandas as pd
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler


class AWSHandlerTestCase(unittest.TestCase):
    
    def setUp(self) -> None:
        self.aws = AWS_handler()
    
    def test_upload_to_s3(self):
        self.aws.clear_s3(prefix='test')
        self.aws.upload_to_s3(path='test/test_files/raw_data', search_name='test')
        self.assertTrue(len(self.aws.list_s3(prefix='test')), 'Error uploading to S3')

    def test_upload_to_rds(self):
        vehicle_data_list = Vehicle_data.parse_json_vehicle_data_list("test/test_files/full_vehicle_data_list.json")
        vehicle_data_list_pd = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list)
        self.aws.upload_to_rds(vehicle_data_list=vehicle_data_list, table='test')
        vehicle_data_list_dl = self.aws.get_table_rds(table='test')
        self.assertTrue(vehicle_data_list_pd.equals(vehicle_data_list_dl), 'Error uploading to RDS')

        
