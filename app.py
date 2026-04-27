import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis_model import get_processed_data

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Retail Revenue Assurance",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished look
st.markdown("""
<style>
    .metric-card {
        background-color: #2e303e;
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA LOADING
# ==========================================
@st.cache_data
def load_data():
    return get_processed_data()

df = load_data()

if df.empty:
    st.error("No data found. Please run data_generator.py first.")
    st.stop()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("PwC Analytics Demo")
st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("Filters")
selected_stores = st.sidebar.multiselect("Select Store(s)", df['Store_ID'].unique(), default=df['Store_ID'].unique())
selected_categories = st.sidebar.multiselect("Select Category(s)", df['Category'].unique(), default=df['Category'].unique())

if 'Region' in df.columns:
    selected_regions = st.sidebar.multiselect("Select Region(s)", df['Region'].unique(), default=df['Region'].unique())
else:
    selected_regions = []

st.sidebar.markdown("---")
st.sidebar.info(
    "**Project Concept:** Revenue Assurance & Forensic Analytics.\n\n"
    "This dashboard detects potential fraudulent refunds/leakage using an Isolation Forest ML algorithm."
)

# Apply filters
if 'Region' in df.columns:
    filtered_df = df[
        (df['Store_ID'].isin(selected_stores)) & 
        (df['Category'].isin(selected_categories)) &
        (df['Region'].isin(selected_regions))
    ]
else:
    filtered_df = df[
        (df['Store_ID'].isin(selected_stores)) & 
        (df['Category'].isin(selected_categories))
    ]

# ==========================================
# MAIN DASHBOARD - KPI METRICS
# ==========================================
st.title("🛒 Retail Revenue Assurance Dashboard")

# Top Level Metrics
total_revenue = filtered_df[filtered_df['Transaction_Type'] == 'Sale']['Sales_Amount'].sum()
total_refunds = filtered_df[filtered_df['Transaction_Type'] == 'Refund']['Sales_Amount'].sum()

# Anomalies calculated
anomalies_df = filtered_df[filtered_df['Is_Anomaly'] == True]
leakage_identified = anomalies_df['Sales_Amount'].sum()
num_anomalies = len(anomalies_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Gross Revenue", value=f"${total_revenue:,.2f}")
with col2:
    st.metric(label="Total Refunds", value=f"${total_refunds:,.2f}", delta="- Refunds", delta_color="inverse")
with col3:
    st.metric(label="Suspicious Leakage (ML)", value=f"${leakage_identified:,.2f}", delta="Needs Audit", delta_color="inverse")
with col4:
    st.metric(label="Anomalies Flagged", value=num_anomalies)

st.markdown("---")

# ==========================================
# CHART VISUALIZATIONS
# ==========================================

tab1, tab2, tab3 = st.tabs(["Overview", "Anomaly Detection", "Raw Data Explorer"])

with tab1:
    st.subheader("Sales vs Refunds Over Time")
    
    # Resample by day
    time_df = filtered_df.groupby([filtered_df['Date'].dt.date, 'Transaction_Type'])['Sales_Amount'].sum().reset_index()
    
    fig_time = px.line(time_df, x='Date', y='Sales_Amount', color='Transaction_Type',
                       color_discrete_map={"Sale": "#1f77b4", "Refund": "#ff7f0e"},
                       title="Daily Transaction Volume")
    st.plotly_chart(fig_time, use_container_width=True)
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        # Category breakdown
        cat_df = filtered_df.groupby('Category')['Sales_Amount'].sum().reset_index()
        fig_cat = px.pie(cat_df, values='Sales_Amount', names='Category', title="Revenue by Category", hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_v2:
        # Store breakdown
        store_df = filtered_df.groupby('Store_ID')['Net_Revenue'].sum().reset_index().sort_values('Net_Revenue', ascending=False)
        fig_store = px.bar(store_df, x='Store_ID', y='Net_Revenue', title="Net Revenue by Store")
        st.plotly_chart(fig_store, use_container_width=True)

with tab2:
    st.subheader("Isolation Forest: Anomaly Identification")
    st.write("The model flags transactions that are outliers based on time of day, refund status, and amount. Note the concentration of high-value refunds late at night.")
    
    # Scatter plot showing anomalies
    fig_scatter = px.scatter(
        filtered_df, 
        x="HourOfDay", y="Sales_Amount", color="Is_Anomaly",
        color_discrete_map={False: "#abdda4", True: "#d7191c"},
        hover_data=['Transaction_ID', 'Store_ID', 'Transaction_Type', 'Date'],
        title="Transaction Scatter (Red = Flagged as Anomalous)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Audit Readiness: High-Risk Transactions")
    st.write("Export this list for investigation.")
    
    if len(anomalies_df) > 0:
        display_cols = ['Transaction_ID', 'Date', 'Store_ID', 'Category', 'Transaction_Type', 'Sales_Amount', 'Anomaly_Score']
        if 'Region' in anomalies_df.columns:
            display_cols.insert(3, 'Region')
            
        st.dataframe(
            anomalies_df[display_cols].sort_values('Anomaly_Score'),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No anomalies detected for the current selection!")
