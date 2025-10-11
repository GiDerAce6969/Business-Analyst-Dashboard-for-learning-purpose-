# Real-Time S&P 500 Stock Analysis Pipeline

[![View Live Dashboard](https://img.shields.io/badge/View-Live_Dashboard-2ea44f?style=for-the-badge)](YOUR_PUBLIC_LOOKER_STUDIO_LINK_HERE)

![Screenshot of your final Looker Studio Dashboard](URL_TO_YOUR_DASHBOARD_SCREENSHOT)

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

## ⚙️ How to Run Locally

1.  **Prerequisites:** A Google Cloud Platform account with a configured service account key.
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure:**
    - Place your GCP service account `key.json` file in the root directory.
    - Update the `project_id` and `table_id` variables in `extract_data.py`.
5.  **Run the ETL script:**
    ```bash
    python extract_data.py
    ```
6.  Connect Looker Studio to your new BigQuery table to build the dashboard.
