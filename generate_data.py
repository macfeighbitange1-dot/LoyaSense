import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
NUM_MEMBERS = 100
DAYS_OF_HISTORY = 365
np.random.seed(42)

def generate_sacco_data():
    data = []
    start_date = datetime(2025, 1, 1)

    for member_id in range(1001, 1001 + NUM_MEMBERS):
        # Increased to 35% to ensure a balanced dataset for the model
        is_churner = np.random.random() < 0.35 
        
        for day in range(DAYS_OF_HISTORY):
            current_date = start_date + timedelta(days=day)
            
            # CHURN LOGIC: 
            # If they are a churner, they stop all activity after day 300.
            # This gives the model enough "silence" to detect a statistical drop.
            if not (is_churner and day > 300): 
                if np.random.random() > 0.7: # 30% chance of transaction daily
                    dep = np.random.choice([0, 500, 1000, 2000, 5000])
                    wd = np.random.choice([0, 200, 1500]) if dep == 0 else 0
                    
                    # Only append if a transaction actually occurred
                    if dep > 0 or wd > 0:
                        data.append([member_id, current_date, dep, wd])
            
    df = pd.DataFrame(data, columns=['member_id', 'date', 'deposit', 'withdrawal'])
    
    # Ensure the data directory exists
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
        
    df.to_csv('data/raw_transactions.csv', index=False)
    print(f"✅ Generated {len(df)} transactions in data/raw_transactions.csv")

if __name__ == "__main__":
    generate_sacco_data()