import os
import pandas as pd
from mistralai import Mistral
from flask import Flask

app = Flask(__name__)

# --- CONFIGURATION ---
# We prioritize the Environment Variable for security on Render
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "QiJh8V2kZ3IQL1eYCAnKqJSOJxSHbTyC")
client = Mistral(api_key=MISTRAL_API_KEY)

def get_ai_recommendation(member_id, prob, score):
    """Calls Mistral API to generate a personalized retention pitch."""
    prompt = f"""
    Act as a SACCO Retention Genius. 
    Member ID: {member_id}
    Churn Risk: {prob:.1f}%
    Engagement Score: {score:.2f}
    
    Task: Write a 1-sentence personalized SMS offer. 
    - If Risk > 50%: Offer a 'Priority Loyalty Loan' with 3% interest discount.
    - If Risk < 50%: Offer a 'Standard Loyalty Loan' with 1.5% discount.
    Tone: Professional, urgent, and empathetic. Start the SMS directly.
    """
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Mistral Error: {e}")
        return f"Hello! As a valued member {member_id}, call us for a special Loyalty Loan offer today!"

def run_analysis():
    """The core logic that processes the member list."""
    try:
        if not os.path.exists('data/top_50_loyalty_list.csv'):
            return "Missing results file. Run predict.py first."

        df = pd.read_csv('data/top_50_loyalty_list.csv')
        # Analysis threshold
        high_risk = df[df['churn_probability'] > 0.05].copy()
        
        results = []
        for _, row in high_risk.iterrows():
            member = int(row['member_id'])
            prob = row['churn_probability'] * 100
            score = row['engagement_score']
            
            ai_sms = get_ai_recommendation(member, prob, score)
            results.append(f"Member {member} ({prob:.1f}% risk): {ai_sms}")
        
        return "\n".join(results)
    except Exception as e:
        return f"Analysis Error: {e}"

# --- WEB ROUTES ---

@app.route('/')
def index():
    """Runs the analysis and displays it on the web page."""
    report = run_analysis()
    return f"""
    <h1>LoyaSense Engine: Agentic Action Plan</h1>
    <hr>
    <pre>{report}</pre>
    <br>
    <p><i>Status: Live and Monitoring SACCO Behavioral Velocity.</i></p>
    """

if __name__ == "__main__":
    # Render assigns a dynamic PORT via environment variables
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' allows external access on Render
    app.run(host='0.0.0.0', port=port)