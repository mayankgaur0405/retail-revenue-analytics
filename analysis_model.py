import pandas as pd
from sklearn.ensemble import IsolationForest
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_preprocess_data(filepath="data/retail_transactions.csv"):
    """Loads CSV data and does basic preprocessing."""
    try:
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Extract useful features for our anomaly detection
        df['HourOfDay'] = df['Date'].dt.hour
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        
        # Convert Transaction_Type to a numeric flag 
        # (1 for Refund, 0 for Sale)
        df['IsRefund'] = df['Transaction_Type'].apply(lambda x: 1 if x == 'Refund' else 0)
        
        logger.info(f"Successfully loaded {len(df)} rows.")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

def train_anomaly_detector(df):
    """
    Trains an Isolation Forest model to detect suspicious transactions
    based on the time of transaction, if it's a refund, and the amount.
    """
    logger.info("Training Isolation Forest...")
    
    # We will use HourOfDay, IsRefund, and Sales_Amount to find anomalies
    features = ['HourOfDay', 'IsRefund', 'Sales_Amount']
    X = df[features].copy()
    
    # Fill any potential NaNs just in case
    X = X.fillna(0)
    
    # Initialize Isolation Forest
    # contamination = expected proportion of outliers
    model = IsolationForest(contamination=0.015, random_state=42, n_estimators=100)
    
    # Fit the model and predict (-1 signifies Anomaly, 1 signifies normal)
    df['Anomaly_Label'] = model.fit_predict(X)
    df['Anomaly_Score'] = model.decision_function(X)
    
    # Convert -1/1 to True/False for easier understanding
    df['Is_Anomaly'] = df['Anomaly_Label'] == -1
    
    num_anomalies = df['Is_Anomaly'].sum()
    logger.info(f"Found {num_anomalies} anomalies.")
    
    return df

def get_processed_data():
    df = load_and_preprocess_data("data/retail_transactions.csv")
    if df is not None:
        return train_anomaly_detector(df)
    return pd.DataFrame()
