import boto3 as bot
import os
from datetime import date

from botocore.exceptions import NoCredentialsError
"""
substitute the  local file location as argument 1 
s3 bucket name as argument 2 
desired destination folder name as argument 3 
"""
def upload_folder_to_s3(folder_path, bucket_name, s3_folder=""):

    s3_client = bot.client('s3')

    for root, _, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_file_path = os.path.join(s3_folder, os.path.relpath(local_file_path, folder_path)).replace("\\", "/")

            try:
                s3_client.upload_file(local_file_path, bucket_name, s3_file_path)
                print(f"Uploaded: {local_file_path} to s3://{bucket_name}/{s3_file_path}")
            except NoCredentialsError:
                print("AWS credentials not found. Please configure them.")
                return
            except Exception as e:
                print(f"Failed to upload {local_file_path}: {e}")

# substitute the values as required
folder_path = "local-file-location-here"
bucket_name = "bucket-name-here"
s3_folder = f"{date.today()}"  # Leave empty if not needed



# Method call
upload_folder_to_s3(folder_path,bucket_name,s3_folder)
