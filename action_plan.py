import pandas as pd
from mistralai import Mistral
import os

# Configuration
MISTRAL_API_KEY = "QiJh8V2kZ3IQL1eYCAnKqJSOJxSHbTyC"
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
    Tone: Professional, urgent, and empathetic. Do not use placeholders like [Name]. 
    Start the SMS directly.
    """
    
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Hello! As a valued member {member_id}, call us for a special Loyalty Loan offer today!"

def generate_marketing_memos():
    # Load results from Phase 3
    if not os.path.exists('data/top_50_loyalty_list.csv'):
        print("❌ Error: Missing top_50_loyalty_list.csv. Run predict.py first.")
        return

    df = pd.read_csv('data/top_50_loyalty_list.csv')
    
    # Filter for anyone with at least some risk (> 5% for AI analysis)
    high_risk = df[df['churn_probability'] > 0.05].copy()
    
    print("🤖 LOYASENSE AGENTIC ACTION PLAN (Powered by Mistral)")
    print("="*60)
    
    for _, row in high_risk.iterrows():
        member = int(row['member_id'])
        prob = row['churn_probability'] * 100
        score = row['engagement_score']
        
        # Identify Urgency for the CLI display
        urgency = "CRITICAL" if prob > 50 else "MONITOR"
        
        print(f"🔍 Analyzing Member {member}...")
        
        # Get the AI-generated SMS
        ai_sms = get_ai_recommendation(member, prob, score)
            
        memo = (
            f"[{urgency}] Member {member}\n"
            f"Risk: {prob:.1f}% | Engagement Score: {score:.2f}\n"
            f"Draft SMS: '{ai_sms}'\n"
            + "-"*60
        )
        print(memo)

if __name__ == "__main__":
    generate_marketing_memos()