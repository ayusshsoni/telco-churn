# --- 1. IMPORTS ---
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- 2. SETUP AND DATA LOADING ---

# Set the page configuration for a wide layout and a title
st.set_page_config(layout="wide", page_title="Telco Churn Analysis")

# Define the path to the cleaned data file
DATA_FILE = Path(__file__).parent / 'data' / 'cleaned_telco_customers.csv'

@st.cache_data  # Cache the data loading to improve performance
def load_data():
    """Loads the cleaned Telco churn data from the CSV file."""
    if not DATA_FILE.is_file():
        st.error(f"--- ERROR: Data file not found at {DATA_FILE} ---")
        st.error("Please make sure 'cleaned_telco_customers.csv' is in a 'data' folder next to this script.")
        return None
    
    df = pd.read_csv(DATA_FILE)

    # ✅ Ensure churn_label exists (fix for KeyError)
    if "churn_label" not in df.columns:
        if "Churn" in df.columns:
            df["churn_label"] = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)
        else:
            st.error("❌ Neither 'churn_label' nor 'Churn' column found in dataset. Please re-run the cleaning pipeline.")
            return None

    return df

# Load the data
df = load_data()

# --- 3. THE DASHBOARD INTERFACE ---

# Main title of the dashboard
st.title("📊 Telco Customer Churn Dashboard")

# If data loading fails, stop the app here
if df is None:
    st.stop()

# --- Sidebar for Filters ---
st.sidebar.header("Customer Filters")

# Filter by Contract Type
contract_filter = st.sidebar.multiselect(
    'Select Contract Type',
    options=df['Contract'].unique(),
    default=df['Contract'].unique()
)

# Filter by Internet Service
internet_filter = st.sidebar.multiselect(
    'Select Internet Service',
    options=df['InternetService'].unique(),
    default=df['InternetService'].unique()
)

# Apply filters to the dataframe
filtered_df = df[
    (df['Contract'].isin(contract_filter)) &
    (df['InternetService'].isin(internet_filter))
]

# --- Main Page Content ---

# Key Performance Indicators (KPIs)
overall_churn_rate = df['churn_label'].mean()
segment_churn_rate = filtered_df['churn_label'].mean() if not filtered_df.empty else 0.0

st.header("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers in Segment", f"{len(filtered_df):,}")
col2.metric("Overall Churn Rate", f"{overall_churn_rate:.2%}")
col3.metric("Segment Churn Rate", f"{segment_churn_rate:.2%}", delta=f"{segment_churn_rate - overall_churn_rate:.2%}")

st.markdown("---")  # Visual separator

# Charts
st.header("Visual Analysis")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Interactive bar chart for Churn by Contract Type
    fig_contract = px.histogram(
        filtered_df, 
        x='Contract', 
        color='churn_label', 
        barmode='group',
        title='Churn by Contract Type',
        labels={'churn_label': 'Churn Status'}
    )
    st.plotly_chart(fig_contract, use_container_width=True)

with col_chart2:
    # Interactive bar chart for Churn by Tenure Bucket
    fig_tenure = px.histogram(
        filtered_df, 
        x='tenure_bucket', 
        color='churn_label', 
        barmode='group',
        title='Churn by Tenure',
        labels={'churn_label': 'Churn Status'},
        category_orders={"tenure_bucket": ["0-1 Year", "1-2 Years", "2-4 Years", "4+ Years"]}
    )
    st.plotly_chart(fig_tenure, use_container_width=True)
    
# Display a snippet of the filtered data
st.header("Filtered Customer Data")
st.dataframe(filtered_df.head(10))
