from sqlite3 import Timestamp
from types import NoneType
import boto3
import datetime
import os
import psycopg2
import pandas as pd
import sqlalchemy as db
from tqdm import tqdm

from scraper.aws_password import pw, ACCESS_KEY, SECRET_KEY
from scraper.vehicle_data import Vehicle_data

class AWS_handler:

    def __init__(self) -> None:
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.ckadzi3b9dep.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = pw
        PORT = 5432
        DATABASE = 'autotrader_scraper'   
        self.engine = db.create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.inspector = db.inspect(self.engine)

    def upload_to_rds(self, vehicle_data_list_pd, table) -> None:
        """
        Upload pandas DataFrame to AWS RDS (relational database service) to PostgreSQL database
        Args:
            vehicle_data_list (list{Vehicle_data}): List of vehicle data to upload
            table (str): Table name on RDS
        """
        for i in tqdm(range(1), desc="Uploading table to RDS..."):
            try:
                vehicle_data_list_pd.to_sql(table, self.engine, if_exists='replace')
            except:
                print(table)
                raise TypeError(f"Vehicle data list type: {type(vehicle_data_list_pd)}")

    def get_table_rds(self, table) -> pd.DataFrame:
        """
        Download table from AWS RDS to pandas df
        Args:
            table (str): Table name on RDS
        Returns:
            (pd.DataFrame): Vehicle data list in pd.DataFrame format
        """
        for i in tqdm(range(1), desc="Downloading table from RDS..."):
            try:
                table_result = pd.read_sql_table(table, self.engine).drop('index', axis=1)
                table_result['img'] = table_result['img'].map(lambda img: img[1:-1].split(', '))
            except:
                table_result = None
        return table_result

    def upload_to_s3(self, path='raw_data', bucket='autotraderscraper', folder_name='', verbose=False) -> None:
        """
        Uploads all files in a path to S3 using boto3
        Args:
            path (str): Location of files to upload
            bucket (str): S3 bucket to store data
            verbose (bool): Option to print output to console (default = False)
        """
        session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3_client = session.client('s3')
        file_paths = []
        s3_list = AWS_handler.list_s3(bucket, prefix=folder_name)
        for root, dirs, files in os.walk(path):
            for file in files:
                file_ext = file.split('.')[-1]
                if file_ext not in ['jpg', 'jpeg']: continue # ignore non-image files
                file_paths.append(os.path.join(root, file))
        for file in tqdm(file_paths, desc="Uploading images to S3..."):
            key = os.path.join(folder_name, file)
            if key not in s3_list:
                response = s3_client.upload_file(Filename=file, Bucket=bucket, Key=key)
        if verbose: print(f"{datetime.datetime.now()}: {len(file_paths)} images uploaded")
        s3_client.close()

    def list_s3(self, bucket='autotraderscraper', prefix='')->list:
        """
        Lists all data stored in S3 bucket
        Args:
            bucket (str): S3 bucket to list data
        Returns: 
        """
        session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3_client = session.client('s3')
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
        session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3 = session.resource('s3')
        bkt = s3.Bucket(bucket)
        bkt.objects.filter(Prefix=prefix).delete()

    def upload_list_to_remote(self, vehicle_data_list, table, verbose=False) -> None:
        """
        Args:
            vehicle_data_list (list{Vehicle_data}): List from memory
            table (str): AWS RDS table name to save data
        """
        aws = AWS_handler()
        vehicle_data_list_pd = Vehicle_data.get_pandas_vehicle_data_list(vehicle_data_list)
        vehicle_data_list_remote_pd = aws.get_table_rds(table)
        if type(vehicle_data_list_remote_pd)==NoneType:
            vehicle_data_list_remote_pd = vehicle_data_list_pd.drop(vehicle_data_list_pd.index) # empty pandas table

        updated_vdl = vehicle_data_list_remote_pd

        combined_vdl = pd.merge(vehicle_data_list_pd.drop(columns=['date_scraped', 'last_updated']),
                                vehicle_data_list_remote_pd.drop(columns=['date_scraped', 'last_updated']),
                                how='outer', on='id', indicator=True)

        # Items removed since last search
        rm_ids = combined_vdl.query('_merge == "right_only" and date_removed_y.isnull()', engine='python')
        if not rm_ids.empty:
            rm_vdl = vehicle_data_list_remote_pd[vehicle_data_list_remote_pd.id.isin(rm_ids.id)]
            rm_vdl = rm_vdl.assign(date_removed=datetime.datetime.now())
            updated_vdl = pd.concat([updated_vdl[~updated_vdl.id.isin(rm_vdl.id)], rm_vdl])
        if verbose: print(f"Removed items:\n{rm_ids[['id']].to_string(index=False)}\n")

        # New items:
        new_ids = combined_vdl.query('_merge == "left_only"')
        if not new_ids.empty:
            new_vdl = vehicle_data_list_pd[vehicle_data_list_pd.id.isin(new_ids.id)]
            new_vdl = new_vdl.assign(last_updated=datetime.datetime.now())
            updated_vdl = pd.concat([updated_vdl, new_vdl])
        if verbose: print(f"New items:\n{new_ids[['id']].to_string(index=False)}\n")

        # Items to update:
        common_ids = combined_vdl.query('_merge == "both"')
        if not common_ids.empty:
            duplicate_ids = pd.merge(vehicle_data_list_pd.drop(columns=['date_scraped', 'last_updated', 'date_removed', 'uuid', 'img']),
                                    vehicle_data_list_remote_pd.drop(columns=['date_scraped', 'last_updated', 'date_removed', 'uuid', 'img']),
                                    how='inner')
            modified_ids = common_ids[~common_ids.id.isin(duplicate_ids.id)]
            if not modified_ids.empty:
                modified_vdl = pd.merge(vehicle_data_list_pd[vehicle_data_list_pd.id.isin(modified_ids)].drop(columns=['date_scraped']),
                                    vehicle_data_list_remote_pd[vehicle_data_list_remote_pd.id.isin(modified_ids)][['id', 'date_scraped']],
                                    how='outer', on='id')
                modified_vdl = modified_vdl.assign(last_updated=datetime.datetime.now())
                updated_vdl = pd.concat([updated_vdl[~updated_vdl.id.isin(modified_vdl.id)], modified_vdl])
            if verbose: print(f"Updated items:\n{modified_vdl[['id']].to_string(index=False)}\n")

        aws.upload_to_rds(updated_vdl, table)

if __name__ == "__main__":
    pass