import yfinance as yf
import pandas as pd
from pandas_gbq import to_gbq
import os
import requests # Import the requests library

# --- Configuration ---
# Point to your downloaded service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/content/t-monument-474805-k0-b47f6153c116.json"

# GCP Project and BigQuery details
project_id = "t-monument-474805-k0"
table_id = "stock_data.sp500_daily_data" # Dataset.TableName

# Get the list of S&P 500 tickers
print("Fetching S&P 500 tickers...")

# Add a User-Agent header to the request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# Use requests to get the page content with headers, then pass it to pandas
response = requests.get(url, headers=headers)
response.raise_for_status() # Raise an exception for bad status codes
sp500_tickers = pd.read_html(response.text)[0]['Symbol'].tolist()

print(f"Found {len(sp500_tickers)} tickers.")

# Fetch 20 years of historical data for all tickers
print("Fetching historical stock data...")
# 'yfinance' can download data for multiple tickers at once
# For very large requests, you might loop and append, but this is often fine
all_data = yf.download(sp500_tickers, start="2004-01-01", end="2024-01-01")

# --- Transformation ---
print("Transforming data...")
# The downloaded data has a multi-level column index, we need to flatten it
df = all_data.stack(level=1).reset_index()
df = df.rename(columns={'level_1': 'Ticker'})

# Calculate financial metrics
df['Moving_Avg_50'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(50).mean())
df['Daily_Return'] = df.groupby('Ticker')['Close'].transform(lambda x: x.pct_change())

# --- Load to BigQuery ---
print(f"Loading {len(df)} rows into BigQuery...")
to_gbq(df,
       destination_table=table_id,
       project_id=project_id,
       if_exists='replace') # Use 'replace' for the first run, 'append' for updates

print("Data loading complete!")
