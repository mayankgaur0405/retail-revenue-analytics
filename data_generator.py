import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_dirty_retail_data(num_records=15000):
    np.random.seed(42)
    random.seed(42)

    categories = ['Electronics', 'Clothing', 'Home Goods', 'Groceries']
    
    # 1. Create Store Dimension Table Data (For SQL JOINs)
    store_data = {
        'Store_ID': [f'STORE_{str(i).zfill(3)}' for i in range(1, 11)],
        'Region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], 10),
        'Manager_Name': [f'Manager_{i}' for i in range(1, 11)]
    }
    df_stores = pd.DataFrame(store_data)

    # 2. Generate Base Transactions Date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    dates = [start_date + timedelta(days=random.randint(0, 180), 
                                    hours=random.randint(8, 22), 
                                    minutes=random.randint(0, 59)) 
             for _ in range(num_records)]
    dates.sort()

    data = {
        'Transaction_ID': [f'TXN_{str(i).zfill(6)}' for i in range(1, num_records + 1)],
        'Date': dates,
        'Store_ID': np.random.choice(store_data['Store_ID'], num_records),
        'Category': np.random.choice(categories, num_records),
        'Sales_Amount': np.round(np.random.gamma(shape=2.0, scale=50.0, size=num_records), 2),
        'Transaction_Type': np.random.choice(['Sale', 'Refund'], num_records, p=[0.95, 0.05]),
        'Customer_ID': [f'CUST_{str(random.randint(1, 5000)).zfill(4)}' for _ in range(num_records)]
    }
    df = pd.DataFrame(data)

    # ==========================================
    # INJECTING DIRTY DATA (For ETL Cleaning Step)
    # ==========================================
    
    # A. Missing Values (NULLs)
    null_indices = random.sample(range(num_records), int(num_records * 0.05)) # 5% missing sales
    df.loc[null_indices, 'Sales_Amount'] = np.nan
    
    null_cat_indices = random.sample(range(num_records), int(num_records * 0.02)) # 2% missing categories
    df.loc[null_cat_indices, 'Category'] = None

    # B. Exact Duplicate Rows
    duplicates = df.sample(n=int(num_records * 0.03)) # 3% hard duplicates
    df = pd.concat([df, duplicates], ignore_index=True)

    # C. Introduce ML Anomalies (Fraudulent Refunds / Late night activity)
    num_anomalies = int(num_records * 0.015) 
    anomaly_indices = random.sample(range(len(df)), num_anomalies)
    
    for idx in anomaly_indices:
        df.at[idx, 'Transaction_Type'] = 'Refund'
        df.at[idx, 'Sales_Amount'] = round(random.uniform(500, 2000), 2)
        df.at[idx, 'Date'] = df.at[idx, 'Date'].replace(hour=random.choice([0, 1, 2, 3]))

    # ==========================================
    # LOAD INTO SQLITE RELATIONAL DATABASE
    # ==========================================
    os.makedirs('data', exist_ok=True)
    db_path = 'data/retail_db.sqlite'
    
    if os.path.exists(db_path):
        os.remove(db_path) # Fresh DB each run
        
    conn = sqlite3.connect(db_path)
    
    # Create tables
    df_stores.to_sql('stores', conn, if_exists='replace', index=False)
    df.to_sql('raw_transactions', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"Generated {len(df)} transactions (including injected duplicates and nulls).")
    print(f"Data successfully saved to SQLite Database: {db_path}")

if __name__ == "__main__":
    generate_dirty_retail_data(15000)
