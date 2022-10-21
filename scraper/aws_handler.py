import boto3
import datetime
import os
import psycopg2
import pandas as pd
import aws_password
import sqlalchemy as db
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
        self.engine = db.create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.s3_client = boto3.client('s3')

    def create_rds(self, table) -> None:
        """
        Creates SQL table for vehicle data info
        Args:
            table (string): Name of table (car make/model)
        """
        metadata = db.MetaData()
        rds_table = db.Table(table, metadata, 
                            db.Column('id', db.Integer, primary_key = True),
                            db.Column('uuid', db.String),
                            db.Column('date_added', db.DateTime),
                            db.Column('last_updated', db.DateTime),
                            db.Column('date_removed', db.DateTime),
                            db.Column('href', db.String),
                            db.Column('title', db.String),
                            db.Column('subtitle', db.String),
                            db.Column('price', db.Integer),
                            db.Column('location', db.String),
                            db.Column('mileage', db.Integer),
                            db.Column('description', db.String),
                            db.Column('img', db.String)
                            ) 
        metadata.create_all(self.engine)

    def add_to_rds(self, vehicle_data, table) -> None:
        """
        Adds Vehicle_data object to remote SQL table. Compares row with existing entries, and uploads or updates the row.
        Args:
            vehicle_data (Vehicle_data): Vehicle data object describing the SQL row to upload
            table (str): Name to SQL table to upload
        """
        veh_id = vehicle_data.get_data()['id']
        remote_data =  self.engine.execute(f"SELECT * FROM {table} WHERE id = \'{veh_id}\'").fetchall()
        if not remote_data: #if entry does not exist
            values = [v for k,v in vehicle_data.get_data(flattened=True).items()]
            values_txt = f"{values[0]}"
            for i in range(1, len(values)):
                values_txt += f", \'{values[i]}\'"
            with self.engine.connect() as conn:
                conn.execute(f"INSERT INTO {table} VALUES ({values_txt})")
        elif len(remote_data) > 1:
            print(remote_data)
            raise Exception(f"Multiple matches found in remote database: {table}")
        else: #compare data entries and update on rds
            cols_to_ignore = ['date_scraped', 'last_updated', 'date_removed']
            remote_data = pd.DataFrame(remote_data).set_index('id').drop(cols_to_ignore, axis=1)
            vehicle_data = vehicle_data.get_data_pd().drop(cols_to_ignore, axis=1)
            cols_to_update = list(vehicle_data.compare(remote_data, align_axis=0).columns)
            if cols_to_update:
                update_txt = ""
                for col in cols_to_update:
                    update_txt += f"{col} = \'{vehicle_data[col].loc[veh_id]}\', "
                with self.engine.connect() as conn:
                    conn.execute(f"UPDATE {table} SET {update_txt.strip().strip(',')} WHERE id=\'{veh_id}\'")
                    conn.execute(f"UPDATE {table} SET last_updated=\'{datetime.datetime.now()}\' WHERE id=\'{veh_id}\'")

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
        for vehicle_data in tqdm(vehicle_data_list, desc="Uploading data to RDS..."):
            self.add_to_rds(vehicle_data, table)

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