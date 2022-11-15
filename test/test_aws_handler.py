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
        self.aws.upload_to_s3(path='test/test_files/raw_data', folder_name='test')
        self.assertTrue(len(self.aws.list_s3(prefix='test')), 'Error uploading to S3')

    def test_upload_to_rds(self):
        vehicle_data_list = Vehicle_data.parse_json_vehicle_data_list("test/test_files/full_vehicle_data_list.json")
        vehicle_data_list_pd = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list).drop(['last_updated', 'date_removed'], axis=1)
        self.aws.upload_to_rds(vehicle_data_list_pd, 'test')
        vehicle_data_list_remote_pd = self.aws.get_table_rds(table='test')
        self.assertTrue(vehicle_data_list_pd.equals(vehicle_data_list_remote_pd), 'Error uploading to RDS')
        self.aws.engine.execute('DROP TABLE test')

    def test_upload_to_remote(self):
        """
        Check data is uploaded to remote
        """
        vehicle_data_list = Vehicle_data.parse_json_vehicle_data_list("test/test_files/full_vehicle_data_list.json")
        try: self.aws.engine.execute('DROP TABLE test')
        except: pass
        self.aws.upload_list_to_remote(vehicle_data_list, 'test')
        
        # Manual manipulation of test data
        vdl0_id = vehicle_data_list[0].get_data()['id']
        vdl1_id = vehicle_data_list[1].get_data()['id']
        vdl2_id = vehicle_data_list[2].get_data()['id']
        vdl3_id = '88888888'

        vehicle_data_list[0].add_data(title='Updated Car')
        vehicle_data_list.remove(vehicle_data_list[1])
        vd_3 = Vehicle_data(vdl3_id)
        vehicle_data_list.append(vd_3)

        self.aws.upload_list_to_remote(vehicle_data_list, 'test')

        vdl_remote = self.aws.get_table_rds('test')
        self.aws.engine.execute('DROP TABLE test')
        self.assertTrue([vdl0_id, vdl1_id, vdl2_id, vdl3_id] in vdl_remote['id'].values, "RDS database does not match")

        
