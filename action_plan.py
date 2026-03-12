import os
import pandas as pd
import subprocess
from flask import Flask, request, render_template

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
    Act as a Financial Retention Genius. 
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
        return response.choices[0].message.content.strip().replace('"', "'") 
    except Exception as e:
        return f"Hello Member {member_id}, we have a special Loyalty Loan discount for you!"

def run_analysis():
    """Processes data with a 100% Dark Theme injection and graceful error handling."""
    file_path = 'data/top_50_loyalty_list.csv'
    raw_input_path = 'data/raw_input.csv'
    
    # --- PRE-FLIGHT CHECK ---
    if not os.path.exists(file_path):
        # Attempt to auto-generate if input exists
        if os.path.exists(raw_input_path) or os.path.exists('data/member_features.csv'):
            try:
                subprocess.run(["python", "predict.py"], check=True)
            except Exception as e:
                return f"<div class='alert' style='background:#7f1d1d; color:white;'>System Sync Error: {e}</div>"
        else:
            # High-end empty state for new users/deployments
            return """
            <div class="text-center py-5" style="border: 1px dashed #1e293b; border-radius: 15px; background: rgba(34, 211, 238, 0.02); margin-top: 20px;">
                <i class="fas fa-database mb-3 text-muted" style="font-size: 2.5rem; opacity: 0.3;"></i>
                <h5 class="text-white fw-bold">Neural Engine Offline</h5>
                <p class="text-muted small">Please upload member transaction logs to initiate the intelligence layer.</p>
            </div>
            """

    try:
        df = pd.read_csv(file_path)
        total_analyzed = len(df)
        
        critical_count = len(df[df['churn_probability'] > 0.8])
        high_risk_count = len(df[(df['churn_probability'] > 0.5) & (df['churn_probability'] <= 0.8)])
        monitor_count = len(df[(df['churn_probability'] > 0.05) & (df['churn_probability'] <= 0.5)])

        # 1. EXECUTIVE SUMMARY (Midnight Themed)
        summary_html = f"""
        <div class="alert shadow-lg border-0 mb-4" style="background: #0f172a; color: #f1f5f9; border: 1px solid #1e293b !important; border-radius: 15px;">
            <div class="row text-center py-2">
                <div class="col-md-3 border-end border-secondary border-opacity-25">
                    <small class="text-uppercase opacity-50" style="font-size: 0.7rem;">Scanned</small>
                    <h3 class="fw-bold mb-0" style="color: #22d3ee;">{total_analyzed}</h3>
                </div>
                <div class="col-md-3 border-end border-secondary border-opacity-25">
                    <small class="text-uppercase" style="font-size: 0.7rem; color: #ff4d4d;">Critical</small>
                    <h3 class="fw-bold mb-0" style="color: #ff4d4d;">{critical_count}</h3>
                </div>
                <div class="col-md-3 border-end border-secondary border-opacity-25">
                    <small class="text-uppercase" style="font-size: 0.7rem; color: #fbbf24;">High Risk</small>
                    <h3 class="fw-bold mb-0" style="color: #fbbf24;">{high_risk_count}</h3>
                </div>
                <div class="col-md-3">
                    <small class="text-uppercase" style="font-size: 0.7rem; color: #38bdf8;">Monitor</small>
                    <h3 class="fw-bold mb-0" style="color: #38bdf8;">{monitor_count}</h3>
                </div>
            </div>
        </div>
        <h4 class="mb-4 fw-bold text-white"><i class="fas fa-satellite-dish me-2 text-info"></i>Active Retention Missions</h4>
        """

        df = df.sort_values(by='churn_probability', ascending=False)
        high_risk = df[df['churn_probability'] > 0.05].copy()
        
        if high_risk.empty:
            return summary_html + "<p class='text-muted text-center'>✅ Neural scan complete. All members stable.</p>"

        html_cards = summary_html
        for _, row in high_risk.iterrows():
            member = int(row['member_id'])
            prob = row['churn_probability'] * 100
            score = row['engagement_score']
            ai_sms = get_ai_recommendation(member, prob, score)
            
            if prob > 80:
                badge, badge_style, border_color = "CRITICAL", "background: #7f1d1d; color: #fecaca;", "#ef4444"
            elif prob > 50:
                badge, badge_style, border_color = "HIGH RISK", "background: #78350f; color: #fef3c7;", "#f59e0b"
            else:
                badge, badge_style, border_color = "MONITOR", "background: #1e3a8a; color: #dbeafe;", "#3b82f6"

            html_cards += f"""
            <div class="card mb-4" style="background: #0f172a; border: 1px solid #1e293b; border-left: 5px solid {border_color}; border-radius: 12px;">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h5 class="fw-bold text-white mb-0">Member {member}</h5>
                            <span class="text-muted small">Risk Vector: {prob:.1f}%</span>
                        </div>
                        <span class="badge rounded-pill px-3 py-2" style="{badge_style}">{badge}</span>
                    </div>
                    
                    <div class="row mb-3 g-0 rounded" style="background: #020617; border: 1px solid #1e293b;">
                        <div class="col-6 border-end border-secondary border-opacity-25 p-3 text-center">
                            <small class="text-muted d-block text-uppercase" style="font-size: 0.6rem;">Churn Prob</small>
                            <span class="fw-bold h5 text-white">{prob:.1f}%</span>
                        </div>
                        <div class="col-6 p-3 text-center">
                            <small class="text-muted d-block text-uppercase" style="font-size: 0.6rem;">Engage Score</small>
                            <span class="fw-bold h5 text-white">{score:.2f}</span>
                        </div>
                    </div>

                    <div class="p-3 mb-3 rounded" style="background: rgba(34, 211, 238, 0.03); border: 1px dashed #1e293b;">
                        <small class="d-block text-info fw-bold mb-1" style="font-size: 0.7rem;"><i class="fas fa-comment-dots me-1"></i> AI PROPOSED COMMUNICATION:</small>
                        <span class="text-white" style="font-style: italic;">"{ai_sms}"</span>
                    </div>

                    <div class="d-flex gap-2 justify-content-end">
                        <button class="btn btn-sm" style="background: #1e293b; color: #94a3b8; border: 1px solid #334155;" onclick="navigator.clipboard.writeText('{ai_sms}')">
                            <i class="fas fa-copy me-1"></i> Copy
                        </button>
                        <a href="https://wa.me/?text={ai_sms}" target="_blank" class="btn btn-sm px-4" style="background: #059669; color: white;">
                            <i class="fab fa-whatsapp me-1"></i> Deploy
                        </a>
                    </div>
                </div>
            </div>
            """
        return html_cards
    except Exception as e:
        return f"<div class='alert' style='background:#7f1d1d; color:white;'>Data Engine Error: {e}</div>"

@app.route('/', methods=['GET', 'POST'])
def index():
    status_msg = ""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                file.save(os.path.join(UPLOAD_FOLDER, 'raw_input.csv'))
                try:
                    subprocess.run(["python", "predict.py"], check=True)
                    status_msg = "✅ Log Ingested. Neural model updated."
                except:
                    status_msg = "❌ Error: Prediction engine failure."
            else:
                status_msg = "❌ Protocol Error: CSV file required."

    report_html = run_analysis()
    return render_template('dashboard.html', report_html=report_html, status_msg=status_msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)