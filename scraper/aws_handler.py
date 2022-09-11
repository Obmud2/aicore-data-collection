import boto3
import os

class AWS_handler:

    @staticmethod
    def upload_to_s3(path, bucket='autotraderscraper'):

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
                print(f"Uploading file {count} of {num_files}: {file_path}")
                response = s3_client.upload_file(file_path, bucket, file_path)
                count += 1

    @staticmethod
    def list_s3(bucket='autotraderscraper'):
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket('autotraderscraper')
        for file in my_bucket.objects.all():
            print(file.key)

if __name__ == "__main__":
    AWS_handler.upload_to_s3('raw_data')
    AWS_handler.list_s3()