import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="E-commerce Sales & Customer Dashboard",
    page_icon="🛒",
    layout="wide"
)

# --- Caching ---
@st.cache_data
def load_data(path: str):
    """
    Load and preprocess the e-commerce data.
    """
    df = pd.read_csv(path, encoding="ISO-8859-1")
    
    # --- Data Cleaning and Preprocessing ---
    # Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    # Drop rows with missing Customer ID
    df.dropna(subset=['Customer ID'], inplace=True)
    # Ensure Customer ID is an integer
    df['Customer ID'] = df['Customer ID'].astype(int)
    # Remove returns (invoices starting with 'C')
    df = df[~df['Invoice'].str.startswith('C', na=False)]
    # Calculate TotalPrice
    df['TotalPrice'] = df['Quantity'] * df['Price']
    
    return df

# --- RFM Analysis ---
def create_rfm_df(df):
    """
    Create the RFM (Recency, Frequency, Monetary) dataframe.
    """
    # Use a snapshot date for recency calculation (day after the last transaction)
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
    
    # Calculate RFM metrics
    rfm_df = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalPrice': 'MonetaryValue'})
    
    # Create RFM segments using quintiles
    rfm_df['R_Quintile'] = pd.qcut(rfm_df['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm_df['F_Quintile'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_df['M_Quintile'] = pd.qcut(rfm_df['MonetaryValue'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    rfm_df['RFM_Score'] = rfm_df['R_Quintile'].astype(str) + rfm_df['F_Quintile'].astype(str) + rfm_df['M_Quintile'].astype(str)
    
    # Define RFM segments
    segment_map = {
        r'[1-2][1-2]': 'Hibernating',
        r'[1-2][3-4]': 'At Risk',
        r'[1-2]5': 'Cannot Lose Them',
        r'3[1-2]': 'About to Sleep',
        r'33': 'Need Attention',
        r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising',
        r'51': 'New Customers',
        r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions'
    }
    
    rfm_df['Segment'] = rfm_df['R_Quintile'].astype(str) + rfm_df['F_Quintile'].astype(str)
    rfm_df['Segment'] = rfm_df['Segment'].replace(segment_map, regex=True)
    
    return rfm_df

# --- Main Application ---
st.title("🛒 E-commerce Performance Dashboard")
st.markdown("This dashboard provides insights into sales trends and customer segmentation using RFM analysis.")

# Load data
df = load_data('data/online_retail_II.csv')

# --- Sidebar Filters ---
st.sidebar.header("Filters")
min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Convert dates to datetime for filtering
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Apply date filter
filtered_df = df[(df['InvoiceDate'] >= start_datetime) & (df['InvoiceDate'] <= end_datetime)]

# --- KPI Section ---
st.header("Overall Performance")
total_revenue = filtered_df['TotalPrice'].sum()
total_orders = filtered_df['Invoice'].nunique()
total_customers = filtered_df['Customer ID'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Unique Customers", f"{total_customers:,}")

# --- Tabs for Detailed Analysis ---
tab1, tab2 = st.tabs(["Sales Analysis", "Customer Segmentation (RFM)"])

with tab1:
    st.header("Monthly Sales Trend")
    # Resample data to get monthly sales
    monthly_sales = filtered_df.set_index('InvoiceDate')['TotalPrice'].resample('M').sum().reset_index()
    monthly_sales['InvoiceDate'] = monthly_sales['InvoiceDate'].dt.strftime('%Y-%m')
    
    fig_sales = px.bar(monthly_sales, x='InvoiceDate', y='TotalPrice',
                       title="Monthly Revenue", labels={'InvoiceDate': 'Month', 'TotalPrice': 'Revenue'})
    st.plotly_chart(fig_sales, use_container_width=True)

with tab2:
    st.header("RFM Customer Segmentation")
    if not filtered_df.empty:
        rfm_analysis_df = create_rfm_df(filtered_df)
        
        # Display segment distribution
        st.subheader("Customer Segment Distribution")
        segment_counts = rfm_analysis_df['Segment'].value_counts()
        
        fig_segments = px.treemap(names=segment_counts.index, parents=[""]*len(segment_counts), values=segment_counts.values,
                                 title="Distribution of Customers by Segment",
                                 color=segment_counts.values, colorscale='Blues')
        fig_segments.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_segments, use_container_width=True)

        # Allow user to select a segment to inspect
        st.subheader("Deep Dive into a Segment")
        selected_segment = st.selectbox("Select a Segment", rfm_analysis_df['Segment'].unique())
        
        segment_customers = rfm_analysis_df[rfm_analysis_df['Segment'] == selected_segment].sort_values(by='MonetaryValue', ascending=False)
        st.write(f"Displaying top 10 customers from the '{selected_segment}' segment.")
        st.dataframe(segment_customers.head(10))

    else:
        st.warning("No data available for the selected date range to perform RFM analysis.")
