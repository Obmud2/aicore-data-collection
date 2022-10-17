from ctypes import BigEndianStructure
import boto3
import os
import psycopg2
import pandas as pd
import aws_password
from sqlalchemy import create_engine, inspect
from tqdm import tqdm
from scraper.vehicle_data import Vehicle_data

class AWS_handler:

    def __init__(self) -> None:
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.ckadzi3b9dep.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = aws_password.pw
        PORT = 5432
        DATABASE = 'autotrader_scraper'   
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.s3_client = boto3.client('s3')

    def upload_to_rds(self, vehicle_data_list, table) -> None:
        """
        Upload to AWS RDS (relational database service) to PostgreSQL database
        Args:
            vehicle_data_list (list{Vehicle_data}): List of vehicle data to upload
            table (str): Table name on RDS
        Returns:
            (list): Query * from RDS database
        """
        df = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list)
        for i in tqdm(range(1), desc="Uploading data to RDS..."):
            df.to_sql(table, self.engine, if_exists='replace')

    def get_table_rds(self, table) -> pd.DataFrame:
        """
        Download table from AWS RDS to pandas df
        Args:
            table (str): Table name on RDS
        Returns:
            (pd.DataFrame): Vehicle data list in pd.DataFrame format
        """
        for i in tqdm(range(1), desc="Downloading table from RDS..."):
            self.engine.connect()
            table_result = pd.read_sql_table(table, self.engine).set_index('id')
            table_result['img'] = table_result['img'].map(lambda img: img[1:-1].split(', '))
        return table_result

    def upload_to_s3(self, path='raw_data', bucket='autotraderscraper', search_name='', verbose=False) -> None:
        """
        Uploads all files in a path to S3 using boto3
        Args:
            path (str): Location of files to upload
            bucket (str): S3 bucket to store data
            verbose (bool): Option to print output to console (default = False)
        """

        s3_client = boto3.client('s3')
        file_paths = []
        s3_list = AWS_handler.list_s3(bucket, prefix=search_name)
        for root, dirs, files in os.walk(path):
            for file in files:
                file_ext = file.split('.')[-1]
                if file_ext not in ['jpg', 'jpeg']: continue # ignore non-image files
                file_paths.append(os.path.join(root, file))
        for file in tqdm(file_paths, desc="Uploading images to S3..."):
            key = os.path.join(search_name, file)
            if key not in s3_list:
                response = s3_client.upload_file(Filename=file, Bucket=bucket, Key=key)
        s3_client.close()

    def list_s3(self, bucket='autotraderscraper', prefix='')->list:
        """
        Lists all data stored in S3 bucket
        Args:
            bucket (str): S3 bucket to list data
        Returns: 
        """
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        list_files = []
        if 'Contents' in response.keys():
            for file in response['Contents']:
                list_files.append(file['Key'])
        s3_client.close()
        return list_files

    def clear_s3(self, prefix, bucket='autotraderscraper') -> None:
        """
        Clears S3 bucket with given prefix
        Args:
            prefix (str): Name of prefix to delete all files
            bucket (str): Name of bucket
        """
        s3 = boto3.resource('s3')
        bkt = s3.Bucket(bucket)
        bkt.objects.filter(Prefix=prefix).delete()

if __name__ == "__main__":
    pass