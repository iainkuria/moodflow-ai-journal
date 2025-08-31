import os
import json
import hmac
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from openai import OpenAI
from intasend import APIService
from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
CORS(app)

# API Configuration
HF_API_KEY = os.getenv('HF_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INTASEND_PUBLISHABLE_KEY = os.getenv('INTASEND_PUBLISHABLE_KEY')
INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize IntaSend
service = APIService(token=INTASEND_SECRET_KEY, publishable_key=INTASEND_PUBLISHABLE_KEY, test=True)

# Database setup
def init_db():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            sentiment_label VARCHAR(20),
            sentiment_score FLOAT,
            premium_unlocked BOOLEAN DEFAULT FALSE,
            premium_analysis TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_db_connection():
    conn = sqlite3.connect('journal.db')
    conn.row_factory = sqlite3.Row
    return conn

def analyze_sentiment(text):
    """Analyze sentiment using Hugging Face API"""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        response = requests.post(api_url, headers=headers, json={"inputs": text})
        result = response.json()
        
        if response.status_code == 200 and result:
            # Extract the highest scoring sentiment
            if isinstance(result, list) and len(result) > 0:
                sentiment = max(result[0], key=lambda x: x['score'])
                return sentiment['label'], sentiment['score']
        
        return "NEUTRAL", 0.5
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return "NEUTRAL", 0.5

def generate_ai_insight(entry_content, sentiment_label):
    """Generate AI insight using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate and insightful life coach. Provide supportive, actionable insights based on journal entries."
                },
                {
                    "role": "user",
                    "content": f"Act as a compassionate and insightful coach. The user wrote this journal entry: '{entry_content}'. Their overall sentiment was {sentiment_label}. Provide a short, helpful, and kind comment to help them reflect. Keep it under 150 words and make it personal and encouraging."
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Unable to generate insight at this time. Please try again later."

def verify_intasend_signature(payload, signature, secret):
    """Verify IntaSend webhook signature"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/entry', methods=['POST'])
def create_entry():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Analyze sentiment
        sentiment_label, sentiment_score = analyze_sentiment(text)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO journal_entries (content, sentiment_label, sentiment_score, premium_unlocked)
            VALUES (?, ?, ?, ?)
        ''', (text, sentiment_label, sentiment_score, False))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # Get the created entry
        cursor.execute('SELECT * FROM journal_entries WHERE id = ?', (entry_id,))
        entry = dict(cursor.fetchone())
        conn.close()
        
        return jsonify(entry)
    
    except Exception as e:
        print(f"Error creating entry: {e}")
        return jsonify({'error': 'Failed to create entry'}), 500

@app.route('/api/entries', methods=['GET'])
def get_entries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM journal_entries ORDER BY date_created DESC')
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(entries)
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return jsonify({'error': 'Failed to fetch entries'}), 500

@app.route('/api/create-payment-link', methods=['POST'])
def create_payment_link():
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return jsonify({'error': 'Entry ID is required'}), 400
        
        # Create payment link using IntaSend
        payment_data = {
            "amount": 50,  # KES 50
            "currency": "KES",
            "reference": f"moodflow_insight_{entry_id}",
            "callback_url": f"{request.host_url}api/payment-webhook",
            "redirect_url": f"{request.host_url}?payment=success",
            "metadata": {
                "entry_id": str(entry_id),
                "product": "premium_insight"
            }
        }
        
        response = service.collect.payment_link(**payment_data)
        
        if response.get('invoice_url'):
            return jsonify({'payment_url': response['invoice_url']})
        else:
            return jsonify({'error': 'Failed to create payment link'}), 500
            
    except Exception as e:
        print(f"Payment link error: {e}")
        return jsonify({'error': 'Payment service unavailable'}), 500

@app.route('/api/payment-webhook', methods=['POST'])
def payment_webhook():
    try:
        # Get the raw payload and signature
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-IntaSend-Signature', '')
        
        # Verify signature (in production, always verify!)
        if not verify_intasend_signature(payload, signature, INTASEND_SECRET_KEY):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse the webhook data
        webhook_data = request.get_json()
        
        # Check if payment was successful
        if webhook_data.get('state') == 'COMPLETE':
            # Extract entry_id from metadata
            metadata = webhook_data.get('metadata', {})
            entry_id = metadata.get('entry_id')
            
            if entry_id:
                # Update the database to unlock premium for this entry
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE journal_entries 
                    SET premium_unlocked = TRUE 
                    WHERE id = ?
                ''', (entry_id,))
                conn.commit()
                conn.close()
                
                print(f"Premium unlocked for entry {entry_id}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@app.route('/api/generate-insight', methods=['POST'])
def generate_insight():
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return jsonify({'error': 'Entry ID is required'}), 400
        
        # Get the entry from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM journal_entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
        
        if not entry:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        
        entry = dict(entry)
        
        # Check if premium is unlocked
        if not entry['premium_unlocked']:
            conn.close()
            return jsonify({'error': 'Premium not unlocked for this entry'}), 402
        
        # Check if insight already exists
        if entry['premium_analysis']:
            conn.close()
            return jsonify({'insight': entry['premium_analysis']})
        
        # Generate new insight
        insight = generate_ai_insight(entry['content'], entry['sentiment_label'])
        
        # Save the insight
        cursor.execute('''
            UPDATE journal_entries 
            SET premium_analysis = ? 
            WHERE id = ?
        ''', (insight, entry_id))
        conn.commit()
        conn.close()
        
        return jsonify({'insight': insight})
    
    except Exception as e:
        print(f"Insight generation error: {e}")
        return jsonify({'error': 'Failed to generate insight'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)