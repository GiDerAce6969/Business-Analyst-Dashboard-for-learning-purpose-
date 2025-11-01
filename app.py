import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
# Set the page configuration for your Streamlit app.
# This should be the first Streamlit command in your script.
st.set_page_config(
    page_title="Dynamic Sales & Profit Dashboard",
    page_icon="💼",  # You can use emojis as icons
    layout="wide"     # Use the full page width
)

# --- DATA LOADING AND PREPROCESSING ---
@st.cache_data  # Cache the data loading to improve performance
def load_data(file_source):
    """
    Load data from a file source (can be a path or an uploaded file object).
    Handles both CSV and Excel files and performs essential preprocessing.
    """
    try:
        # Determine the file type and load the data accordingly
        if isinstance(file_source, str):  # If it's a string, it's a file path
            file_name = file_source
        else:  # Otherwise, it's an uploaded file object from Streamlit
            file_name = file_source.name

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_source, encoding="ISO-8859-1")
        elif file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_source, engine='openpyxl')
        else:
            st.error("Unsupported file format. Please use a CSV or Excel file.")
            return None

        # --- DATA CLEANING AND PREPARATION ---
        # Standardize column names for consistency (e.g., 'Order Date' -> 'order_date')
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')

        # Find the correct date column dynamically
        date_col = next((col for col in df.columns if 'order_date' in col), None)
        if not date_col:
            st.error("Could not find an 'Order Date' column in the data.")
            return None
        
        # Convert the date column to datetime objects, coercing errors
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        # Drop any rows where the date conversion resulted in a null value
        df.dropna(subset=[date_col], inplace=True)

        # Create a 'month_year' column for time-series analysis
        df['month_year'] = df[date_col].dt.to_period('M').astype(str)
        
        return df

    except Exception as e:
        st.error(f"Error processing the file: {e}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("Dashboard Controls")
    
    # File uploader allows users to upload their own data
    uploaded_file = st.file_uploader(
        "Upload your CSV or Excel file",
        type=['csv', 'xls', 'xlsx']
    )
    st.info(
        """
        **Note:** If no file is uploaded, the dashboard will use the 
        sample 'Superstore' dataset. Your own file should contain columns like 
        'Order Date', 'Sales', 'Profit', 'Region', 'Category', etc.
        """
    )

# --- LOAD DATA (either uploaded or default sample) ---
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    # Load the default sample data if no file is uploaded
    df = load_data("data/Sample - Superstore.xls")


# --- MAIN DASHBOARD (runs only if data is loaded successfully) ---
if df is not None and not df.empty:
    # Rename columns to a consistent format for dashboard logic
    df.rename(columns={
        'region': 'Region', 'category': 'Category', 'segment': 'Segment', 
        'sales': 'Sales', 'profit': 'Profit', 'sub_category': 'Sub-Category',
        'state': 'State', 'month_year': 'Month-Year'
    }, inplace=True, errors='ignore')

    # --- Sidebar Filters (dynamically created from the loaded data) ---
    st.sidebar.header("Dashboard Filters")
    region = st.sidebar.multiselect("Select Region:", options=df['Region'].unique(), default=df['Region'].unique())
    category = st.sidebar.multiselect("Select Category:", options=df['Category'].unique(), default=df['Category'].unique())
    segment = st.sidebar.multiselect("Select Segment:", options=df['Segment'].unique(), default=df['Segment'].unique())

    # Apply filters to the DataFrame
    df_filtered = df[
        df['Region'].isin(region) &
        df['Category'].isin(category) &
        df['Segment'].isin(segment)
    ]

    # --- MAIN DASHBOARD LAYOUT ---
    st.title("📊 Dynamic Sales & Profitability Dashboard")
    st.markdown("---")

    # KPIs
    total_sales = int(df_filtered['Sales'].sum())
    total_profit = int(df_filtered['Profit'].sum())
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Sales", f"US $ {total_sales:,}")
    with col2: st.metric("Total Profit", f"US $ {total_profit:,}")
    with col3: st.metric("Profit Margin", f"{profit_margin:.2f}%")

    st.markdown("---")

    # --- VISUALIZATIONS ---
    st.header("Monthly Sales & Profit Trend")
    monthly_analysis = df_filtered.groupby('Month-Year').agg({'Sales':'sum', 'Profit':'sum'}).reset_index()
    fig_monthly = px.line(monthly_analysis, x='Month-Year', y=['Sales', 'Profit'], title="Sales and Profit Over Time")
    fig_monthly.update_layout(xaxis={'type': 'category'})
    st.plotly_chart(fig_monthly, use_container_width=True)

    col_cat, col_subcat = st.columns(2)
    with col_cat:
        st.header("Sales by Category")
        sales_by_category = df_filtered.groupby('Category')['Sales'].sum().sort_values(ascending=False)
        fig_cat_sales = px.bar(sales_by_category, orientation='h', text_auto='.2s', title="Total Sales by Category")
        st.plotly_chart(fig_cat_sales, use_container_width=True)

    with col_subcat:
        st.header("Profit by Sub-Category")
        profit_by_subcat = df_filtered.groupby('Sub-Category')['Profit'].sum().sort_values(ascending=True)
        fig_subcat_profit = px.bar(profit_by_subcat, orientation='h', text_auto='.2s', title="Total Profit by Sub-Category")
        # Conditionally color bars: green for profit, red for loss
        fig_subcat_profit.update_traces(marker_color=['#2ca02c' if x >= 0 else '#d62728' for x in profit_by_subcat.values])
        st.plotly_chart(fig_subcat_profit, use_container_width=True)

    st.header("Geographical Performance")
    sales_by_state = df_filtered.groupby('State')['Sales'].sum().reset_index()
    fig_geo = px.choropleth(sales_by_state, locations='State', locationmode="USA-states", color='Sales', scope="usa", title="Total Sales by State")
    st.plotly_chart(fig_geo, use_container_width=True)

    # Display the filtered data in an expandable table
    with st.expander("View Raw Data Table"):
        st.dataframe(df_filtered)

else:
    # This message shows when the app starts or if a file fails to load
    st.title("📊 Dynamic Sales & Profitability Dashboard")
    st.info("Please upload a file to begin, or use the default sample data.")
