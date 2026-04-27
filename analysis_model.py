import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_etl_pipeline(db_filepath="data/retail_db.sqlite"):
    """
    Executes the full Extract, Transform, and Load (ETL) pipeline logic.
    """
    
    # ==========================================
    # 1. EXTRACT (SQL Integration)
    # ==========================================
    logger.info("Starting EXTRACT phase...")
    try:
        conn = sqlite3.connect(db_filepath)
        
        # We explicitly write an optimized SQL query using JOIN to fetch dimension data.
        # This matches PwC requirements for SQL extraction logic.
        extract_query = """
            SELECT 
                t.Transaction_ID,
                t.Date,
                t.Store_ID,
                s.Region,
                t.Category,
                t.Sales_Amount,
                t.Transaction_Type,
                t.Customer_ID
            FROM raw_transactions t
            LEFT JOIN stores s ON t.Store_ID = s.Store_ID
        """
        raw_df = pd.read_sql(extract_query, conn)
        
        # -------------------------------------------------------------
        # 💡 INTERVIEW NOTE: If asked to demo advanced SQL aggregations
        # This is how you calculate total store revenue strictly in SQL
        # -------------------------------------------------------------
        analytic_query = """
            SELECT 
                s.Region,
                t.Store_ID, 
                SUM(t.Sales_Amount) as Total_Revenue
            FROM raw_transactions t
            JOIN stores s ON t.Store_ID = s.Store_ID
            WHERE t.Transaction_Type = 'Sale'
            GROUP BY s.Region, t.Store_ID
            HAVING SUM(t.Sales_Amount) > 5000
        """
        analytic_df = pd.read_sql(analytic_query, conn)
        logger.info(f"Test Analytic Query Retrieved {len(analytic_df)} grouped records.")
        # -------------------------------------------------------------

        conn.close()
        logger.info(f"Extracted {len(raw_df)} rows from SQLite.")
    except Exception as e:
        logger.error(f"Error during Extract: {e}")
        return pd.DataFrame()

    # ==========================================
    # 2. TRANSFORM (Data Cleaning)
    # ==========================================
    logger.info("Starting TRANSFORM phase...")
    df = raw_df.copy()
    
    # A. Drop Exact Duplicates
    initial_len = len(df)
    df = df.drop_duplicates(subset=['Transaction_ID'], keep='first')
    logger.info(f"Dropped {initial_len - len(df)} exact duplicate transactions.")
    
    # B. Handle Missing Values / Null Imputation
    # Fill missing Sales_Amount with the median value of its specific Category to prevent skewing
    df['Sales_Amount'] = df.groupby('Category')['Sales_Amount'].transform(lambda x: x.fillna(x.median()))
    
    # Fill completely missing categories with a placeholder attribute
    df['Category'] = df['Category'].fillna('Unknown')
    logger.info("Imputed missing values for Sales_Amount and Category fields.")
    
    # C. Standardize Data Types & Feature Engineering
    df['Date'] = pd.to_datetime(df['Date'])
    df['HourOfDay'] = df['Date'].dt.hour
    
    # Create binary encoding for ML processing (1 = Refund, 0 = Sale)
    df['IsRefund'] = df['Transaction_Type'].apply(lambda x: 1 if x == 'Refund' else 0)
    
    # Correctly identify actual net revenue
    df['Net_Revenue'] = df.apply(lambda row: -row['Sales_Amount'] if row['IsRefund'] == 1 else row['Sales_Amount'], axis=1)

    # ==========================================
    # 3. LOAD (Machine Learning & Analytics Storage)
    # ==========================================
    logger.info("Starting LOAD phase (Applying ML Model)...")
    
    # To detect fraudulent refunds, we look at Time of Day, Refund Status, and Amount.
    features = ['HourOfDay', 'IsRefund', 'Sales_Amount']
    X = df[features].copy()
    X = X.fillna(0) # Absolute safety catch
    
    # Unsupervised Anomaly Detection
    model = IsolationForest(contamination=0.015, random_state=42, n_estimators=100)
    df['Anomaly_Label'] = model.fit_predict(X)
    df['Anomaly_Score'] = model.decision_function(X)
    
    # Convert metric for easier dashboard consumption
    df['Is_Anomaly'] = df['Anomaly_Label'] == -1
    
    num_anomalies = df['Is_Anomaly'].sum()
    logger.info(f"ETL Complete. Loaded results with {num_anomalies} flagged anomalies.")
    
    # Export clean, processed data strictly for Power BI Dashboard Integration
    powerbi_path = "data/powerbi_processed_export.csv"
    df.to_csv(powerbi_path, index=False)
    logger.info(f"Saved processed data to {powerbi_path} for Power BI ingestion.")
    
    # In a true enterprise environment, this returning DataFrame would be written 
    # back into an SQL 'Processed_Data' table. Here, we feed it directly to Streamlit.
    return df

def get_processed_data():
    return run_etl_pipeline("data/retail_db.sqlite")

if __name__ == "__main__":
    df = run_etl_pipeline("data/retail_db.sqlite")
    print(df.head())
