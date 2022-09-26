import boto3
import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

class AWS_handler:

    @staticmethod
    def upload_to_s3(path, bucket='autotraderscraper', verbose=True) -> None:
        """
        Uploads all files in a path to S3 using boto3
        Args:
            path (str): Location of files to upload
            bucket (str): S3 bucket to store data
            verbose (bool): Option to print output to console (default = True)
        """
        def count_files(path) -> int:
            count = 0
            for root, dirs, files in os.walk(path):
                count += len(files)
            return count
        
        count = 1
        num_files = count_files(path)
        s3_client = boto3.client('s3')
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if verbose: print(f"Uploading file {count} of {num_files}: {file_path}")
                response = s3_client.upload_file(file_path, bucket, file_path)
                count += 1

    @staticmethod
    def upload_to_rds(df, db='autotrader_scraper') -> list:
        """
        Upload to AWS RDS (relational database service) to PostgreSQL database
        Args:
            df (pandas.DataFrame): Dataframe to upload
            db (str): Database name on RDS
        Returns:
            (list): Query * from RDS database
        """
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.ckadzi3b9dep.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'george101'
        PORT = 5432
        DATABASE = db

        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        df.to_sql('autotrader', engine, if_exists='replace')
        return engine.execute('''SELECT * FROM autotrader''').fetchall()

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