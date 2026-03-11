import pandas as pd
import joblib
import os

def generate_loyalty_list():
    # 1. PATH CONFIGURATION
    # We prioritize 'raw_input.csv' (from the upload portal)
    input_path = 'data/raw_input.csv'
    if not os.path.exists(input_path):
        # Fallback to default features if no upload exists
        input_path = 'data/member_features.csv'

    model_path = 'models/churn_model.pkl'
    output_path = 'data/top_50_loyalty_list.csv'

    # 2. LOAD MODEL AND DATA
    if not os.path.exists(model_path):
        print(f"❌ Error: Model not found at {model_path}.")
        return

    if not os.path.exists(input_path):
        print(f"❌ Error: No data file found to analyze.")
        return

    # Loading the model
    model = joblib.load(model_path)

    # LOAD DATA WITH ENCODING FALLBACK (The Genius Fix)
    try:
        # Try standard UTF-8 first (standard for most modern systems)
        data = pd.read_csv(input_path, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback for Excel-style CSVs or files with special currency/regional characters
        print("⚠️ UTF-8 Decode failed, trying latin1 encoding fallback...")
        data = pd.read_csv(input_path, encoding='latin1')

    # 3. FEATURE PREPARATION
    # Ensure columns match what the model was trained on
    required_cols = ['deposit', 'withdrawal', 'engagement_score']
    
    # Simple check: if columns are missing, we can't predict
    for col in required_cols:
        if col not in data.columns:
            print(f"⚠️ Warning: Missing column '{col}'. Filling with 0.")
            data[col] = 0

    features = data[required_cols]

    # 4. PREDICT PROBABILITIES
    if len(model.classes_) > 1:
        # Index 1 is usually the probability of 'True' (Churn)
        probabilities = model.predict_proba(features)[:, 1]
    else:
        print("⚠️ Warning: Model only knows one class. Setting prob to 0.")
        probabilities = [0.0] * len(data)

    # 5. ATTACH AND RANK
    data['churn_probability'] = probabilities
    
    # Sort: Highest Churn Risk first, then Lowest Engagement
    hit_list = data.sort_values(
        by=['churn_probability', 'engagement_score'], 
        ascending=[False, True]
    ).head(50)

    # 6. SAVE ACTIONABLE LIST
    # Ensure 'is_flagged' exists for the CSV output
    if 'is_flagged' not in hit_list.columns:
        hit_list['is_flagged'] = hit_list['churn_probability'] > 0.5

    hit_list[['member_id', 'churn_probability', 'engagement_score', 'is_flagged']].to_csv(output_path, index=False)
    
    print(f"🚀 Success! Agentic list generated from: {input_path}")
    print(f"📍 Action plan saved to: {output_path}")

if __name__ == "__main__":
    generate_loyalty_list()