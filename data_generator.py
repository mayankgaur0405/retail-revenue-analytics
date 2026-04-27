import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_retail_data(num_records=10000):
    np.random.seed(42)
    random.seed(42)

    categories = ['Electronics', 'Clothing', 'Home Goods', 'Groceries']
    store_ids = [f'STORE_{str(i).zfill(3)}' for i in range(1, 11)] # 10 stores
    
    # Generate dates over the last 6 months
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
        'Store_ID': np.random.choice(store_ids, num_records),
        'Category': np.random.choice(categories, num_records),
        'Sales_Amount': np.round(np.random.gamma(shape=2.0, scale=50.0, size=num_records), 2),
        'Transaction_Type': np.random.choice(['Sale', 'Refund'], num_records, p=[0.95, 0.05]),
        'Customer_ID': [f'CUST_{str(random.randint(1, 5000)).zfill(4)}' for _ in range(num_records)]
    }

    df = pd.DataFrame(data)

    # Introduce Anomalies (Fraudulent Refunds / High Sales)
    # Anomaly 1: A few huge refunds at unusual times
    num_anomalies = int(num_records * 0.01) # 1% anomalies
    anomaly_indices = random.sample(range(num_records), num_anomalies)
    
    for idx in anomaly_indices:
        df.at[idx, 'Transaction_Type'] = 'Refund'
        df.at[idx, 'Sales_Amount'] = round(random.uniform(500, 2000), 2)
        # Shift time to late night (suspicious)
        df.at[idx, 'Date'] = df.at[idx, 'Date'].replace(hour=random.choice([0, 1, 2, 3]))

    # Calculate net revenue (if refund, value is negative)
    df['Net_Revenue'] = df.apply(lambda row: -row['Sales_Amount'] if row['Transaction_Type'] == 'Refund' else row['Sales_Amount'], axis=1)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/retail_transactions.csv', index=False)
    print(f"Generated {num_records} transaction records with {num_anomalies} anomalies.")
    print("Data saved to 'data/retail_transactions.csv'.")

if __name__ == "__main__":
    generate_retail_data(15000)
