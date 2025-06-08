import os
import schedule
import time
import json
import boto3
import sqlalchemy
from Assignment.lib import dbutils, secretsutil


def run_job():
    AWS_SECRET_NAME = "secret-gtf-mmt-apse1-dev-user-db-secret-01-cicdbmgr"
    secrets = secretsutil.get_secret(AWS_SECRET_NAME, region_name="ap-southeast-1")

    data = json.loads(secrets)
    db_username = data['username']
    db_password = data['password']
    db_host = "aurora-mysql-gtf-mmt-apse1-dev-insurance-01-cluster.cluster-cd3khmkgi258.ap-southeast-1.rds.amazonaws.com"
    db_staging = "staging"
    db_modeled = "modeled"
    ddl_path = "sqlscripts/DataModel.sql"
    bucket_name = "dcp-s3-test-bucket-tf-dev"

    process_date = "2025-06-04"  # or use: f"{datetime.date.today()}"

    model_engine = sqlalchemy.create_engine(
        f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_modeled}")
    staging_engine = sqlalchemy.create_engine(
        f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_staging}")

    try:
        dbutils.staging_data_ingest_from_s3_folder(bucket_name, process_date, staging_engine)
        dbutils.create_model_from_ddl_file(ddl_path, model_engine)
        dbutils.ingest_into_model_from_staging(staging_engine, model_engine, process_date)
        print("Job completed successfully.")
    except Exception as e:
        print(f"Error during job execution: {e}")


# Schedule to run daily at 08:00 AM
schedule.every().day.at("20:15").do(run_job)

print("Scheduler started. Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(60)
