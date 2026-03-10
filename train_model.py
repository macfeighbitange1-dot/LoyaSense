import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def train_churn_predictor():
    # 1. Load the synthesized features
    df = pd.read_csv('data/member_features.csv')
    
    # 2. Define Features (X) and Target (y)
    # We use deposit, withdrawal, and engagement_score to predict the flag
    X = df[['deposit', 'withdrawal', 'engagement_score']]
    y = df['is_flagged']
    
    # 3. Split into Training (80%) and Testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Initialize and Train the Random Forest
    print("🧠 Training the LoyaSense Brain...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    print("\n--- Model Performance Report ---")
    print(classification_report(y_test, y_pred))
    
    # 6. Save the model
    joblib.dump(model, 'models/churn_model.pkl')
    print("✅ Model saved to models/churn_model.pkl")

if __name__ == "__main__":
    train_churn_predictor()