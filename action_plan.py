import os
import pandas as pd
import subprocess
from flask import Flask, request

# Robust Mistral Import
try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import MistralClient as Mistral

app = Flask(__name__)

# --- CONFIGURATION ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "QiJh8V2kZ3IQL1eYCAnKqJSOJxSHbTyC")
UPLOAD_FOLDER = 'data'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize client
try:
    client = Mistral(api_key=MISTRAL_API_KEY)
except Exception as e:
    print(f"Initialization Error: {e}")
    client = None

def get_ai_recommendation(member_id, prob, score):
    """Calls Mistral API for personalized SMS."""
    if not client:
        return f"Hello Member {member_id}, visit our branch for a special Loyalty Loan offer today!"

    prompt = f"""
    Act as a SACCO Retention Genius. 
    Member ID: {member_id} | Churn Risk: {prob:.1f}% | Engagement: {score:.2f}
    Task: Write a 1-sentence personalized SMS offer. 
    - If Risk > 50%: Offer 'Priority Loyalty Loan' (3% discount).
    - If Risk < 50%: Offer 'Standard Loyalty Loan' (1.5% discount).
    Tone: Professional and urgent.
    """
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Hello Member {member_id}, we have a special Loyalty Loan discount for you!"

def run_analysis():
    """Processes data and returns color-coded HTML results."""
    file_path = 'data/top_50_loyalty_list.csv'
    
    if not os.path.exists(file_path):
        try:
            subprocess.run(["python", "predict.py"], check=True)
        except Exception as e:
            return f"<p style='color:red;'>System Error: {e}</p>"

    try:
        df = pd.read_csv(file_path)
        df = df.sort_values(by='churn_probability', ascending=False)
        high_risk = df[df['churn_probability'] > 0.05].copy()
        
        if high_risk.empty:
            return "<p>✅ All members are currently stable.</p>"

        html_cards = ""
        for _, row in high_risk.iterrows():
            member = int(row['member_id'])
            prob = row['churn_probability'] * 100
            score = row['engagement_score']
            ai_sms = get_ai_recommendation(member, prob, score)
            
            # Priority Badges
            if prob > 80:
                badge, color = "CRITICAL", "#e74c3c"
            elif prob > 50:
                badge, color = "HIGH RISK", "#f39c12"
            else:
                badge, color = "MONITOR", "#3498db"

            html_cards += f"""
            <div style="background:white; border-left: 6px solid {color}; padding:15px; margin-bottom:15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between;">
                    <strong>Member {member}</strong>
                    <span style="background:{color}; color:white; padding:2px 8px; border-radius:4px; font-size:0.75em; font-weight:bold;">{badge}</span>
                </div>
                <div style="font-size:0.85em; color:#666; margin:5px 0;">Churn Risk: {prob:.1f}% | Score: {score:.2f}</div>
                <div style="background:#fdfdfd; border:1px solid #eee; padding:10px; margin-top:8px; border-radius:4px; font-style:italic;">"{ai_sms}"</div>
            </div>
            """
        return html_cards
    except Exception as e:
        return f"Data Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    status_msg = ""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                # In your predict.py, ensure it reads 'data/raw_input.csv'
                file.save(os.path.join(UPLOAD_FOLDER, 'raw_input.csv'))
                try:
                    subprocess.run(["python", "predict.py"], check=True)
                    status_msg = "✅ Upload successful. Model re-trained."
                except:
                    status_msg = "❌ Error running prediction."

    report_html = run_analysis()
    
    return f"""
    <html>
        <head>
            <title>LoyaSense AI | Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>body{{background:#f4f7f6; font-family:'Segoe UI',sans-serif;}} .container{{max-width:800px; margin:auto; padding:20px;}}</style>
        </head>
        <body>
            <div class="container">
                <div style="background:#1a73e8; color:white; padding:30px; border-radius:12px; margin-bottom:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <h1 style="margin:0;">LoyaSense Engine</h1>
                    <p style="opacity:0.9;">Predictive Churn Analysis & Agentic SMS Generation</p>
                    
                    <form method="post" enctype="multipart/form-data" style="margin-top:20px; background:rgba(255,255,255,0.1); padding:15px; border-radius:8px;">
                        <label style="display:block; margin-bottom:10px; font-weight:bold;">Upload Latest Member Data (CSV):</label>
                        <input type="file" name="file" accept=".csv" style="font-size:0.9em;">
                        <input type="submit" value="Analyze Now" style="background:white; color:#1a73e8; border:none; padding:8px 15px; border-radius:4px; font-weight:bold; cursor:pointer;">
                    </form>
                    <p style="font-size:0.9em; margin-top:10px;">{status_msg}</p>
                </div>

                <h3 style="color:#2c3e50; border-bottom:2px solid #ddd; padding-bottom:10px;">Priority Retention Plan</h3>
                {report_html}
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)