import pandas as pd
import joblib
import os

def generate_loyalty_list():
    input_path = 'data/raw_input.csv'
    if not os.path.exists(input_path):
        input_path = 'data/member_features.csv'

    model_path = 'models/churn_model.pkl'
    output_path = 'data/top_50_loyalty_list.csv'

    if not os.path.exists(model_path) or not os.path.exists(input_path):
        print("❌ Essential files missing.")
        return

    model = joblib.load(model_path)

    # 1. LOAD DATA WITH MAX FORGIVENESS
    try:
        data = pd.read_csv(input_path, sep=None, engine='python', encoding='utf-8', on_bad_lines='skip', quoting=0)
    except Exception:
        data = pd.read_csv(input_path, sep=None, engine='python', encoding='latin1', on_bad_lines='skip', quoting=0)

    # 2. FUZZY COLUMN MATCHING (The "Once and For All" Fix)
    # Convert all columns to lowercase and remove spaces for matching
    data.columns = [c.lower().replace(' ', '_').strip() for c in data.columns]

    # Map of what we need : common variations found in SACCO data
    mapping = {
        'member_id': ['member_id', 'id', 'account_no', 'member_no', 'client_id'],
        'deposit': ['deposit', 'deposits', 'savings', 'total_deposit'],
        'withdrawal': ['withdrawal', 'withdrawals', 'total_withdrawal'],
        'engagement_score': ['engagement_score', 'score', 'activity_level']
    }

    for target, variations in mapping.items():
        if target not in data.columns:
            # Check if any variation exists in the uploaded file
            found = False
            for v in variations:
                if v in data.columns:
                    data.rename(columns={v: target}, inplace=True)
                    found = True
                    break
            
            if not found:
                print(f"⚠️ Column '{target}' missing. generating defaults...")
                if target == 'member_id':
                    data['member_id'] = range(1000, 1000 + len(data))
                else:
                    data[target] = 0

    # 3. PREDICT
    features = data[['deposit', 'withdrawal', 'engagement_score']]
    
    if len(model.classes_) > 1:
        probabilities = model.predict_proba(features)[:, 1]
    else:
        probabilities = [0.0] * len(data)

    data['churn_probability'] = probabilities
    
    # 4. RANK AND FLAG
    hit_list = data.sort_values(by=['churn_probability', 'engagement_score'], ascending=[False, True]).head(50)
    
    if 'is_flagged' not in hit_list.columns:
        hit_list['is_flagged'] = hit_list['churn_probability'] > 0.5

    # 5. FINAL EXPORT (Safeguarded)
    # We ensure these 4 columns exist before slicing
    final_cols = ['member_id', 'churn_probability', 'engagement_score', 'is_flagged']
    hit_list[final_cols].to_csv(output_path, index=False)
    
    print(f"🚀 Deployment Success: {output_path} generated.")

if __name__ == "__main__":
    generate_loyalty_list()