import pandas as pd

def calculate_engagement_score(df):
    # 1. Group by Member and Month to see trends
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby(['member_id', 'month']).agg({
        'deposit': 'sum',
        'withdrawal': 'sum'
    }).reset_index()

    # 2. Apply the Genius Formula: E = Deposits / (Withdrawals + 1)
    monthly['engagement_score'] = monthly['deposit'] / (monthly['withdrawal'] + 1)

    # 3. Calculate Sigma Signal
    stats = monthly.groupby('member_id')['engagement_score'].agg(['mean', 'std']).reset_index()
    
    # Handle members with only one month of data (where std is NaN)
    stats['std'] = stats['std'].fillna(0)
    
    # 4. Identify the "Drop"
    latest_month = monthly.sort_values('month').groupby('member_id').tail(1)
    merged = pd.merge(latest_month, stats, on='member_id')
    
    # GENIUS TUNING: 1.0 * std for sensitivity
    merged['is_flagged'] = (merged['engagement_score'] < (merged['mean'] - 1.0 * merged['std'])) & (merged['std'] > 0)
    
    return merged

if __name__ == "__main__":
    # UPDATE: Now attempts to read from Excel (member_data.xlsx) first, falls back to CSV
    try:
        import os
        if os.path.exists('data/member_data.xlsx'):
            raw_df = pd.read_excel('data/member_data.xlsx', parse_dates=['date'])
            print("📊 Loaded data from member_data.xlsx")
        else:
            raw_df = pd.read_csv('data/raw_transactions.csv', parse_dates=['date'])
            print("📄 Loaded data from raw_transactions.csv")

        feature_df = calculate_engagement_score(raw_df)
        feature_df.to_csv('data/member_features.csv', index=False)
        
        flagged_count = feature_df['is_flagged'].sum()
        print(f"🚀 Features synthesized. Identified {flagged_count} potential churners.")
    except Exception as e:
        print(f"❌ Error: {e}")