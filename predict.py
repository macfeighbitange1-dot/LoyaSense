import pandas as pd
import joblib
import os

def generate_loyalty_list():
    # 1. Load the Model and the Latest Data
    if not os.path.exists('models/churn_model.pkl'):
        print("❌ Error: Model not found. Run train_model.py first.")
        return

    model = joblib.load('models/churn_model.pkl')
    data = pd.read_csv('data/member_features.csv')

    # 2. Predict Probabilities
    features = data[['deposit', 'withdrawal', 'engagement_score']]
    
    # GENIUS FIX: Check how many classes the model actually knows
    # If it only knows 'False' (1 class), index 1 will crash.
    if len(model.classes_) > 1:
        probabilities = model.predict_proba(features)[:, 1]
    else:
        # If model only saw 'False', probability of churn is 0.0 for everyone
        print("⚠️  Warning: Model only trained on 'Loyal' data. Probability set to 0.")
        probabilities = [0.0] * len(data)

    # 3. Attach scores to the member list
    data['churn_probability'] = probabilities
    
    # 4. Filter and Rank the "Top 50"
    # We sort by probability (high to low) and then by engagement (low to high)
    hit_list = data.sort_values(by=['churn_probability', 'engagement_score'], 
                                ascending=[False, True]).head(50)

    # 5. Save the Actionable List
    output_path = 'data/top_50_loyalty_list.csv'
    # Adding 'is_flagged' so the marketing team can see the statistical signal
    hit_list[['member_id', 'churn_probability', 'engagement_score', 'is_flagged']].to_csv(output_path, index=False)
    
    print(f"🚀 Success! The 'Loyalty Loan' target list is ready.")
    print(f"📍 Saved to: {output_path}")
    print("\n--- Sample of Top At-Risk Members ---")
    print(hit_list[['member_id', 'churn_probability', 'is_flagged']].head(10))

if __name__ == "__main__":
    generate_loyalty_list()