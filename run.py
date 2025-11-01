import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests # <-- IMPORT THIS LIBRARY

# --- Page Configuration ---
st.set_page_config(
    page_title="S&P 500 BI Dashboard",
    page_icon="💼",
    layout="wide"
)

# --- Caching Functions ---

@st.cache_resource
def get_sp500_tickers():
    """
    Scrapes S&P 500 tickers from Wikipedia with a User-Agent header.
    Includes a fallback list to ensure the app is always functional.
    """
    try:
        # Define a browser-like User-Agent header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        
        # Make the request with the specified header
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        
        # Pass the HTML content of the response to pandas
        table = pd.read_html(response.text)
        tickers = table[0]['Symbol'].tolist()
        return sorted(tickers)
    
    except Exception as e:
        st.error(f"Could not fetch S&P 500 tickers from Wikipedia: {e}. Using a fallback list.")
        # Fallback list in case the scrape fails
        return sorted([
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'JPM', 'JNJ', 'V', 'PG',
            'UNH', 'HD', 'MA', 'BAC', 'DIS', 'PFE', 'XOM', 'CSCO', 'PEP', 'KO',
            'ADBE', 'CRM', 'NFLX', 'INTC', 'T', 'WMT', 'MCD', 'NKE', 'ABT', 'MDT'
        ])

@st.cache_data(ttl=timedelta(hours=1))
def get_stock_data(tickers, start_date, end_date):
    """
    Downloads historical stock data for a list of tickers from Yahoo Finance.
    """
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)
        if data.empty:
            st.warning("No data found for the selected tickers and date range.")
            return pd.DataFrame()
        return data
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        return pd.DataFrame()

# --- Main Application ---

st.title("📈 S&P 500 Business Intelligence Dashboard")
st.markdown("Analyze and compare S&P 500 stocks with interactive charts and key metrics.")

# --- Sidebar for User Controls ---
st.sidebar.header("Dashboard Controls")

sp500_tickers = get_sp500_tickers()

if sp500_tickers:
    selected_tickers = st.sidebar.multiselect(
        "Select Stock Tickers",
        sp500_tickers,
        default=['AAPL', 'MSFT', 'GOOGL', 'NVDA']
    )
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365*5))
    with col2:
        end_date = st.date_input("End Date", datetime.today())
    ma_period = st.sidebar.slider("Moving Average Period (Days)", 5, 200, 50)
    normalize_performance = st.sidebar.checkbox("Normalize Performance (Base 100)")
else:
    st.sidebar.warning("Ticker list could not be loaded.")
    selected_tickers = []

# --- Main Panel Display ---
if not selected_tickers:
    st.info("Please select one or more stock tickers from the sidebar to begin analysis.")
else:
    data = get_stock_data(selected_tickers, start_date, end_date)
    if not data.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["Performance Overview", "Key Metrics", "Correlation Matrix", "Raw Data"])
        
        # --- Tab 1: Performance Overview ---
        with tab1:
            st.header("Stock Performance Comparison")
            plot_data = data['Close'].copy()
            if normalize_performance:
                st.subheader("Normalized Performance (Base 100)")
                plot_data = (plot_data / plot_data.iloc[0] * 100)
            else:
                st.subheader("Closing Prices (USD)")
            fig = go.Figure()
            for ticker in selected_tickers:
                # Handle cases where a single ticker is a string, not a list in columns
                if isinstance(plot_data.columns, pd.MultiIndex):
                    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data[ticker], mode='lines', name=ticker))
                else: # When only one ticker is selected, columns are not multi-index
                    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data, mode='lines', name=ticker))
            
            if len(selected_tickers) == 1:
                ticker_symbol = selected_tickers[0]
                ma_data = data['Close'].rolling(window=ma_period).mean()
                if normalize_performance:
                    ma_data = (ma_data / plot_data.iloc[0] * 100)
                fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data, mode='lines', 
                                         name=f'{ma_period}-Day MA', line=dict(dash='dot', color='orange')))

            fig.update_layout(
                yaxis_title="Price (Base 100)" if normalize_performance else "Price (USD)",
                xaxis_title="Date", legend_title="Tickers", hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Tab 2: Key Financial Metrics ---
        with tab2:
            st.header("Key Financial Metrics")
            metrics_list = []
            # Use data['Close'] directly; yfinance multi-ticker download might have multi-level columns
            close_data = data['Close']
            returns_data = close_data.pct_change()

            for ticker in selected_tickers:
                last_close = close_data[ticker].iloc[-1]
                high_52_week = close_data[ticker].rolling(window=252).max().iloc[-1]
                low_52_week = close_data[ticker].rolling(window=252).min().iloc[-1]
                annual_volatility = returns_data[ticker].std() * (252**0.5)
                
                metrics_list.append({
                    "Ticker": ticker, "Last Close": last_close, "52-Week High": high_52_week,
                    "52-Week Low": low_52_week, "Annualized Volatility": annual_volatility
                })
            
            metrics_df = pd.DataFrame(metrics_list).set_index("Ticker")
            st.dataframe(metrics_df.style.format({
                "Last Close": "${:.2f}", "52-Week High": "${:.2f}",
                "52-Week Low": "${:.2f}", "Annualized Volatility": "{:.2%}"
            }))

        # --- Tab 3: Correlation Matrix ---
        with tab3:
            st.header("Stock Correlation Matrix")
            if len(selected_tickers) > 1:
                returns_data = data['Close'].pct_change().dropna()
                corr_matrix = returns_data.corr()
                corr_fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns,
                    colorscale='RdBu', zmin=-1, zmax=1, text=corr_matrix.values,
                    texttemplate="%{text:.2f}"
                ))
                corr_fig.update_layout(title="Correlation of Daily Returns")
                st.plotly_chart(corr_fig, use_container_width=True)
            else:
                st.info("Select at least two stocks to view their correlation.")

        # --- Tab 4: Raw Data ---
        with tab4:
            st.header("Raw Financial Data")
            st.dataframe(data)
