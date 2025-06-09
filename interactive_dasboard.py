import plotly.graph_objs as go
import pandas as pd
import boto3
from io import StringIO

from Assignment.pyplot_dash import load_data_from_s3

s3 = boto3.client('s3')
bucket_name = 'aws-bucket-here'
process_date = '2025-06-05'
policy_file = f"{process_date}/policy.csv"
invoice_file = f"{process_date}/invoice.csv"
claims_file = f"{process_date}/claim.csv"


def total_premium_paid_interactive(df):
    df['charge_date'] = pd.to_datetime(df['charge_date'], errors='coerce')
    df = df.dropna(subset=['charge_date'])
    df['year_month'] = df['charge_date'].dt.to_period('M')
    monthly_premium = df.groupby('year_month')['total_amount'].sum()
    mean_premium = monthly_premium.mean()
    std_premium = monthly_premium.std()
    anomalies = monthly_premium[
        (monthly_premium > mean_premium + 2 * std_premium) | (monthly_premium < mean_premium - 2 * std_premium)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_premium.index.astype(str), y=monthly_premium.values, mode='lines+markers',
                             name='Total Premium Received'))
    fig.add_trace(go.Scatter(x=anomalies.index.astype(str), y=anomalies.values, mode='markers', name='Anomalies',
                             marker=dict(color='red', size=10)))

    fig.update_layout(title='Total Premium Received Per Month with Anomalies Highlighted',
                      xaxis_title='Month',
                      yaxis_title='Total Premium Received',
                      xaxis_tickangle=-45)

    fig.write_html("premium_received_by_month.html")


invoice_df = load_data_from_s3(bucket_name, invoice_file)
# Example usage
total_premium_paid_interactive(invoice_df)
