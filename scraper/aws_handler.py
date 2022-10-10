import boto3
import os
import psycopg2
import pandas as pd
import aws_password
from sqlalchemy import create_engine
from tqdm import tqdm

class AWS_handler:

    @staticmethod
    def upload_to_s3(path='raw_data', bucket='autotraderscraper', search_name='', verbose=False) -> None:
        """
        Uploads all files in a path to S3 using boto3
        Args:
            path (str): Location of files to upload
            bucket (str): S3 bucket to store data
            verbose (bool): Option to print output to console (default = True)
        """
        def count_jpg_files(path) -> int:
            count = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    if ".jpg" in file:
                        count += 1
            return count
        
        count = 1
        num_files = count_jpg_files(path)
        s3_client = boto3.client('s3')
        file_paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == "data.json": continue # ignore json files
                file_paths.append(os.path.join(root, file))
        for file in tqdm(file_paths, desc="Uploading images to S3..."):
            response = s3_client.upload_file(file, bucket, os.path.join(search_name, file))

    @staticmethod
    def upload_to_rds(df, table) -> None:
        """
        Upload to AWS RDS (relational database service) to PostgreSQL database
        Args:
            df (pandas.DataFrame): Dataframe to upload
            table (str): Table name on RDS
        Returns:
            (list): Query * from RDS database
        """
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.ckadzi3b9dep.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = aws_password.pw
        PORT = 5432
        DATABASE = 'autotrader_scraper'

        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        tqdm(df.to_sql(table, engine, if_exists='replace'), desc="Uploading data to RDS...")

    @staticmethod
    def list_s3(bucket='autotraderscraper'):
        """
        Lists all data stored in S3 bucket
        Args:
            bucket (str): S3 bucket to list data
        """
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket)
        for file in my_bucket.objects.all():
            print(file.key)

if __name__ == "__main__":
    df = pd.DataFrame([1,2,3,'test'])
    print(df)
    AWS_handler.upload_to_rds(df)
    #AWS_handler.upload_to_s3('raw_data')
    #AWS_handler.list_s3()