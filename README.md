# Real-Time S&P 500 Stock Analysis Pipeline

[![View Live Dashboard](https://img.shields.io/badge/View-Live_Dashboard-2ea44f?style=for-the-badge)](https://lookerstudio.google.com/u/0/reporting/d5c939cb-83c9-407e-9647-22715763a277/page/DxKbF/edit)



## 📄 Summary

This project demonstrates an end-to-end data pipeline for analyzing large-scale financial data. Over 20 years of daily stock prices for all S&P 500 companies were extracted, processed with Python, and loaded into Google BigQuery. The data is visualized through a dynamic and interactive dashboard built in Google Looker Studio.

---

## 🏛️ Project Architecture

The pipeline follows a modern ETL (Extract, Transform, Load) architecture designed for scalability and performance.

`Python (yfinance, pandas)` -> `Google BigQuery (Data Warehouse)` -> `Google Looker Studio (BI Dashboard)`

---

## 🚀 Key Features

- **Big Data Processing:** Successfully handled and processed over **5 million rows** of historical stock data.
- **Cloud Data Warehousing:** Leveraged **Google BigQuery** for its serverless, highly scalable, and cost-effective data storage capabilities.
- **Automated ETL:** The Python script automates the entire process of fetching, cleaning, calculating metrics, and loading data.
- **Interactive Visualization:** The Looker Studio dashboard allows users to dynamically filter by stock ticker and analyze trends across multiple financial metrics.

---

## 🛠️ Tech Stack

- **Cloud:** Google Cloud Platform (GCP)
- **Data Warehouse:** Google BigQuery
- **Data Extraction:** Python, `yfinance`
- **Data Transformation:** Python, `pandas`
- **BI & Visualization:** Google Looker Studio

---

## 📊 Dashboard Features

The interactive dashboard includes:
- **Ticker-level Filtering:** Analyze any company in the S&P 500.
- **Historical Price and Moving Average:** A time-series chart to track performance and trends.
- **Key Performance Indicators (KPIs):** At-a-glance metrics for price and volume.
- **Daily Return Analysis:** Understand volatility and daily price changes.

---

