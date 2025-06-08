import pandas as pd
import matplotlib.pyplot as plt
import boto3
from io import StringIO

s3 = boto3.client('s3')

bucket_name = 'dcp-s3-test-bucket-tf-dev'
process_date = '2025-06-05'

policy_file = f"{process_date}/policy.csv"
invoice_file = f"{process_date}/invoice.csv"
claims_file = f"{process_date}/claim.csv"

policy_obj = s3.get_object(Bucket=bucket_name, Key=policy_file)
policy_data = policy_obj['Body'].read().decode('utf-8')
policy_df = pd.read_csv(StringIO(policy_data))

invoice_obj = s3.get_object(Bucket=bucket_name, Key=invoice_file)
invoice_data = invoice_obj['Body'].read().decode('utf-8')
invoice_df = pd.read_csv(StringIO(invoice_data))

claims_obj = s3.get_object(Bucket=bucket_name, Key=claims_file)
claims_data = claims_obj['Body'].read().decode('utf-8')
claims_df = pd.read_csv(StringIO(claims_data))


def policy_issued_by_gender_age_product(df):
    df['issue_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
    df['insured_dob'] = pd.to_datetime(df['insured_date_of_birth'], errors='coerce')

    df = df.dropna(subset=['issue_date'])

    df['age'] = (pd.to_datetime('today') - df['insured_dob']).dt.days // 365

    # Define age groups
    bins = [0, 18, 30, 45, 60, 75, 100]
    labels = ['0-18', '19-30', '31-45', '46-60', '61-75', '76-100']

    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

    # Group and count
    age_gender_product_policy_count = df.groupby(['age_group', 'insured_gender', 'product']
                                                 ).size().unstack(fill_value=0)

    # Plot

    age_gender_product_policy_count.plot(kind='bar', stacked=False, figsize=(14, 8))
    plt.title('Number of Policies Issued by Age Group, Gender, and Product Type')
    plt.xlabel('Age Group')
    plt.ylabel('Number of Policies Issued')
    plt.xticks(rotation=45)
    plt.legend(title='Gender and Product Type')
    plt.tight_layout()
    plt.savefig("policy_issued_by_gender_product.png")
    # plt.show()


def total_premium_paid(df):
    # Convert 'charge_date' to datetime
    df['charge_date'] = pd.to_datetime(df['charge_date'], errors='coerce')

    # Filter out rows with invalid dates
    df = df.dropna(subset=['charge_date'])

    # Extract year and month from charge_date
    df['year_month'] = df['charge_date'].dt.to_period('M')

    # Calculate total premium received per month
    monthly_premium = df.groupby('year_month')['total_amount'].sum()

    # Calculate mean and standard deviation for anomaly detection
    mean_premium = monthly_premium.mean()
    std_premium = monthly_premium.std()

    # Identify anomalies (months where premium is more than 2 standard deviations from the mean)
    anomalies = monthly_premium[(monthly_premium > mean_premium + 2 * std_premium) |
                                (monthly_premium < mean_premium - 2 * std_premium)]

    # Plot total premium received per month
    plt.figure(figsize=(14, 8))
    plt.plot(monthly_premium.index.astype(str), monthly_premium.values, marker='o', label='Total Premium Received')
    plt.scatter(anomalies.index.astype(str), anomalies.values, color='red', label='Anomalies', zorder=5)
    plt.title('Total Premium Received Per Month with Anomalies Highlighted')
    plt.xlabel('Month')
    plt.ylabel('Total Premium Received')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("premium_received_by_month.png")
    # plt.show()

    # Plot premium received by invoice status
    status_premium = df.groupby(['year_month', 'status'])['total_amount'].sum().unstack(fill_value=0)

    status_premium.plot(kind='bar', stacked=False, figsize=(14, 8))
    plt.title('Total Premium Received Per Month by Invoice Status')
    plt.xlabel('Month')
    plt.ylabel('Total Premium Received')
    plt.xticks(rotation=45)
    plt.legend(title='Invoice Status')
    plt.tight_layout()
    plt.savefig("premium_received_by_month_by_invoice_status.png")
    # plt.show()


def loss_ratio():
    # Convert policy_number to string and pad with leading zeros to 13 digits
    claims_df['policy_number'] = claims_df['policy_number'].astype(str).str.zfill(13)
    invoice_df['policy_number'] = invoice_df['policy_number'].astype(str).str.zfill(13)

    # Merge the dataframes on policy_number
    merged_df = pd.merge(claims_df, invoice_df, on='policy_number', suffixes=('_claim', '_invoice'))
    merged_df = pd.merge(merged_df, policy_df, on='policy_number')

    # Filter for paid claims and invoices
    paid_df = merged_df[(merged_df['status_claim'] == 'paid') & (merged_df['status_invoice'] == 'paid')]

    # Convert dates to datetime
    paid_df['payment_date'] = pd.to_datetime(paid_df['payment_date'], errors='coerce')
    paid_df['charge_date'] = pd.to_datetime(paid_df['charge_date'], errors='coerce')

    # Extract year from payment_date
    paid_df['year'] = paid_df['payment_date'].dt.year

    # Calculate loss ratio only done for status='paid'
    paid_df['loss_ratio'] = paid_df['total_base_payable_amount'] / paid_df['total_amount']

    # Group by year and product and calculate average loss ratio
    grouped_df = paid_df.groupby(['year', 'product'])['loss_ratio'].mean().unstack(fill_value=0)

    # Plot the average loss ratio per year by product
    grouped_df.plot(kind='bar', figsize=(14, 8))
    plt.title('Average Loss Ratio Per Year by Product')
    plt.xlabel('Year')
    plt.ylabel('Average Loss Ratio')
    plt.xticks(rotation=45)
    plt.legend(title='Product')
    plt.tight_layout()
    plt.savefig("loss_ratio_by_product_per_year.png")
    # plt.show()


try:
    loss_ratio()
    total_premium_paid(invoice_df)
    policy_issued_by_gender_age_product(policy_df)
except Exception as e:
    print(f"Error: {e}")
