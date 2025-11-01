import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="S&P 500 BI Dashboard",
    page_icon="💼",
    layout="wide"
)

# --- Caching Functions ---

@st.cache_resource # Cache the resource, runs only once
def get_sp500_tickers():
    """
    Scrapes the S&P 500 tickers from Wikipedia and caches the result.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url)
        tickers = table[0]['Symbol'].tolist()
        return sorted(tickers)
    except Exception as e:
        st.error(f"Could not fetch S&P 500 tickers: {e}")
        return [] # Return empty list on error

@st.cache_data(ttl=timedelta(hours=1)) # Cache data for 1 hour
def get_stock_data(tickers, start_date, end_date):
    """
    Downloads historical stock data for a list of tickers from Yahoo Finance.
    """
    try:
        # yfinance can download multiple tickers at once
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

# Fetch S&P 500 tickers
sp500_tickers = get_sp500_tickers()

if sp500_tickers:
    # Ticker selection
    selected_tickers = st.sidebar.multiselect(
        "Select Stock Tickers",
        sp500_tickers,
        default=['AAPL', 'MSFT', 'GOOGL', 'NVDA'] # Default selection
    )

    # Date range selection
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365*5)) # Default 5 years
    with col2:
        end_date = st.date_input("End Date", datetime.today())

    # Interactive analysis controls
    ma_period = st.sidebar.slider("Moving Average Period (Days)", 5, 200, 50) # Slider for MA
    normalize_performance = st.sidebar.checkbox("Normalize Performance (Base 100)")

else:
    st.sidebar.warning("Ticker list could not be loaded.")
    selected_tickers = []

# --- Main Panel Display ---
if not selected_tickers:
    st.info("Please select one or more stock tickers from the sidebar to begin analysis.")
else:
    # Download data
    data = get_stock_data(selected_tickers, start_date, end_date)

    if not data.empty:
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["Performance Overview", "Key Metrics", "Correlation Matrix", "Raw Data"])

        # --- Tab 1: Performance Overview ---
        with tab1:
            st.header("Stock Performance Comparison")
            
            # Prepare data for plotting
            plot_data = data['Close'].copy()
            if normalize_performance:
                st.subheader("Normalized Performance (Base 100)")
                # Normalize by dividing each column by its first value
                plot_data = (plot_data / plot_data.iloc[0] * 100)
            else:
                st.subheader("Closing Prices (USD)")

            fig = go.Figure()
            for ticker in selected_tickers:
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data[ticker], mode='lines', name=ticker))
            
            # Add Moving Average only if a single stock is selected
            if len(selected_tickers) == 1:
                ticker_symbol = selected_tickers[0]
                ma_data = data['Close'][ticker_symbol].rolling(window=ma_period).mean()
                if normalize_performance:
                    ma_data = (ma_data / plot_data[ticker_symbol].iloc[0] * 100)
                fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data, mode='lines', 
                                         name=f'{ma_period}-Day MA', line=dict(dash='dot', color='orange')))

            fig.update_layout(
                yaxis_title="Price (Base 100)" if normalize_performance else "Price (USD)",
                xaxis_title="Date",
                legend_title="Tickers",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Tab 2: Key Financial Metrics ---
        with tab2:
            st.header("Key Financial Metrics")
            metrics_list = []
            returns_data = data['Close'].pct_change()

            for ticker in selected_tickers:
                last_close = data['Close'][ticker].iloc[-1]
                high_52_week = data['Close'][ticker].rolling(window=252).max().iloc[-1]
                low_52_week = data['Close'][ticker].rolling(window=252).min().iloc[-1]
                # Annualized Volatility (standard deviation of daily returns * sqrt(252 trading days))
                annual_volatility = returns_data[ticker].std() * (252**0.5)
                
                metrics_list.append({
                    "Ticker": ticker,
                    "Last Close": last_close,
                    "52-Week High": high_52_week,
                    "52-Week Low": low_52_week,
                    "Annualized Volatility": annual_volatility
                })
            
            metrics_df = pd.DataFrame(metrics_list).set_index("Ticker")
            st.dataframe(metrics_df.style.format({
                "Last Close": "${:.2f}",
                "52-Week High": "${:.2f}",
                "52-Week Low": "${:.2f}",
                "Annualized Volatility": "{:.2%}"
            }))

        # --- Tab 3: Correlation Matrix ---
        with tab3:
            st.header("Stock Correlation Matrix")
            if len(selected_tickers) > 1:
                returns_data = data['Close'].pct_change().dropna()
                corr_matrix = returns_data.corr()
                
                corr_fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmin=-1,
                    zmax=1,
                    text=corr_matrix.values,
                    texttemplate="%{text:.2f}"
                ))
                corr_fig.update_layout(title="Correlation of Daily Returns")
                st.plotly_chart(corr_fig, use_container_width=True)
            else:
                st.info("Select at least two stocks to view their correlation.")

        # --- Tab 4: Raw Data ---
        with tab4:
            st.header("Raw Financial Data")
            st.write("Displaying data for all selected tickers.")
            st.dataframe(data)
