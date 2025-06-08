import json
import os

import boto3 as bot
import sqlalchemy
import pandas as pd
from pandasql import sqldf
import io

"""
The file assumes the databases are created in advance

"""


def staging_data_ingest_from_s3_folder(bucket_name, s3_folder,
                                       staging_engine):

    print("Executing : staging_data_ingest_from_s3_folder ")
    """
    Method creates as many tables based on unique files from source S3 folder
    Secrets are retrieved from SecretManger using SecretUtils.py File . This can be replaced with Hardcoded Strings to
    substitute required values

    :param db_username:
    :param db_password:
    :param db_host:
    :param db_staging:
    :param bucket_name:
    :param s3_folder:
    :return:
    """
    s3 = bot.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
    print(bucket_name , s3_folder)
    try:
        if 'Contents' in response:
            for obj in response['Contents']:
                file_key = obj['Key']
                if file_key.endswith('.csv'):
                    print("Files found ")
                    csv_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                    body = csv_obj['Body'].read().decode('utf-8')

                    # Convert CSV content to a DataFrame and pick the tablename as filename (claim,invoice.etc)
                    df = pd.read_csv(io.StringIO(body), dtype={'policy_number': str})
                    df.to_sql(name=file_key.split('/')[1].split('.')[0], con=staging_engine, if_exists='replace',
                              index=False)
        else :
            print("Files Not found ")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_model_from_ddl_file(ddl_path, model_engine):
    try:
        with open(ddl_path, "r") as sql_file:
            sql_script = sql_file.read()
        with model_engine.connect() as conn:
            for sql_statement in sql_script.split(";"):
                if sql_statement.strip():  # Skip empty statements
                    conn.execute(sqlalchemy.text(sql_statement))

        print("SQL script executed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()


def ingest_into_model_from_staging(staging_engine, model_engine, process_date):
    import uuid
    namespace = uuid.NAMESPACE_DNS

    check_policy = f"""
    select id from Policy where process_date='{process_date}' limit 5 
    """

    check_policy_df = pd.read_sql(check_policy, con=model_engine)

    policy_query = """
           SELECT * FROM POLICY 
           """
    policy_df = pd.read_sql(policy_query, con=staging_engine)

    policy_df['policy_uuid'] = policy_df['policy_number'].apply(
        lambda x: str(uuid.uuid5(namespace, f"{x}|{process_date}")))
    policy_df['user_id'] = policy_df['user_id'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}")))
    policy_df['product_id'] = policy_df['product'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}")))
    policy_df['gender_id'] = policy_df['insured_gender'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}")))
    policy_df['policy_id'] = policy_df['policy_number'].apply(lambda x: str(uuid.uuid5(namespace, x)))

    if check_policy_df.empty:

        model_policy_df = sqldf(f"""
            select 
            policy_uuid as id ,
            policy_id  ,
            policy_number,
            user_id,
            application_id,
            product_id,
            insured_date_of_birth,
            gender_id as insured_gender_id,
            issue_date,
            effective_date,
            '{process_date}' as process_date from policy_df 
            """)
        model_policy_df.to_sql(name='policy', con=model_engine, if_exists='append',
                               index=False)
        print("New Policy DataSet Inserted !")

    else:
        print("Policy Data already Exists for Present Day")

    product_df = sqldf(f""" select distinct  product_id as id  ,  product as product,'{process_date}' as process_date from policy_df 
            """)

    # ONly Load if new
    existing_products = pd.read_sql("SELECT id  FROM product", con=model_engine)
    new_products_df = product_df[~product_df['id'].isin(existing_products['id'])]
    new_products_df.to_sql(name='product', con=model_engine, if_exists='append', index=False)
    print("Product Updated!")

    gender_df = sqldf(f"""
                select distinct 
                gender_id as id ,
                insured_gender as gender,
                '{process_date}' as process_date from policy_df 
                """)

    # ONly Lod if new
    existing_gender = pd.read_sql("SELECT id FROM gender", con=model_engine)
    new_genders_df = gender_df[~gender_df['id'].isin(existing_gender['id'])]
    new_genders_df.to_sql(name='gender', con=model_engine, if_exists='append', index=False)
    print("Gender Updated !")

    check_claim = f"""
        select id from Claim where process_date='{process_date}' limit 5
        """

    check_claim_df = pd.read_sql(check_claim, con=model_engine)

    claim_query = """Select * from CLAIM"""

    claim_df = pd.read_sql(claim_query, con=staging_engine)

    claim_df['policy_id'] = claim_df['policy_number'].apply(lambda x: str(uuid.uuid5(namespace, x)))
    claim_df['claim_uuid'] = claim_df['id'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}|{process_date}")))
    claim_df['status_id'] = claim_df['status'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}|CLAIM")))
    claim_df['payment_date_formatted'] = pd.to_datetime(claim_df['payment_date'], format='mixed')
    claim_df['submit_date_formatted'] = pd.to_datetime(claim_df['submit_date'], format='mixed')

    if check_claim_df.empty:

        modeled_claim_df = sqldf(f"""
                select distinct claim_uuid as id ,
                id as claim_id,
                type as type,
                status_id as status_id,
                policy_id as policy_id,
                submit_date_formatted as submit_date,
                payment_date_formatted as payment_date,
                admission_date,
                total_billed_amount AS total_billed_amount,
                total_base_payable_amount AS total_base_payable_amount,
                '{process_date}' as process_date from claim_df  
                """)

        modeled_claim_df.to_sql(name='claim', con=model_engine, if_exists='append',
                                index=False)
        print("New Claim DataSet Inserted !")

    else:
        print("Claim Data already Exists for Present Day")

    check_invoice = f"""
        select id from invoice where process_date='{process_date}' limit 5
        """
    check_invoice_df = pd.read_sql(check_invoice, con=model_engine)
    invoice_query = """Select * from INVOICE"""

    invoice_df = pd.read_sql(invoice_query, con=staging_engine)
    invoice_df['invoice_uuid'] = invoice_df['id'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}|{process_date}")))
    invoice_df['policy_id'] = invoice_df['policy_number'].apply(lambda x: str(uuid.uuid5(namespace, x)))
    invoice_df['coverage_end_date_formatted'] = pd.to_datetime(invoice_df['coverage_end_date'], format='mixed')
    invoice_df['coverage_start_date_formatted'] = pd.to_datetime(invoice_df['coverage_start_date'], format='mixed')
    invoice_df['due_date_formatted'] = pd.to_datetime(invoice_df['due_date'], format='mixed')
    invoice_df['refund_date_formatted'] = pd.to_datetime(invoice_df['refund_date'], format='mixed')
    invoice_df['charge_date_formatted'] = pd.to_datetime(invoice_df['charge_date'], format='mixed')
    invoice_df['status_id'] = invoice_df['status'].apply(lambda x: str(uuid.uuid5(namespace, f"{x}|INVOICE")))

    if check_invoice_df.empty:
        modeled_invoice_df = sqldf(f"""
                select invoice_uuid as id ,
                id as invoice_id,
                invoice_type as invoice_type,
                policy_id as policy_id,
                coverage_start_date_formatted as coverage_start_date,
                coverage_end_date_formatted as coverage_end_date,
                due_date_formatted as due_date,
                status_id ,
                pre_levy_amount as pre_levy_amount,
                total_amount AS total_amount,
                refund_date_formatted AS refund_date,
                charge_date_formatted as charge_date,
                '{process_date}' as process_date from invoice_df  
                """)
        modeled_invoice_df.to_sql(name='invoice', con=model_engine, if_exists='append',
                                  index=False)
        print("New Invoice DataSet Inserted !")


    else:
        print("Invoice Data already Exists for Present Day")

    status_df = sqldf(f"""
                    select distinct status_id as id,
                    status as status,
                    'CLAIM' as module,
                    '{process_date}' as process_date from claim_df 
                    UNION 
                    select distinct status_id as id ,
                    status as status,
                    'INVOICE' as module,
                    '{process_date}' as process_date from invoice_df 
                    """)

    # ONly Load if new
    existing_status = pd.read_sql("SELECT id FROM status", con=model_engine)
    new_status_df = status_df[~status_df['id'].isin(existing_status['id'])]
    new_status_df.to_sql(name='status', con=model_engine, if_exists='append', index=False)

    print("Status Updated !")


