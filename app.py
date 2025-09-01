import os
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import requests
from openai import OpenAI
from intasend import APIService
from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
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
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Update journal_entries table to include user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            sentiment_label VARCHAR(20),
            sentiment_score FLOAT,
            premium_unlocked BOOLEAN DEFAULT FALSE,
            premium_analysis TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Sessions table for better session management
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token VARCHAR(255) NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    if 'user_id' not in session:
        return None
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ? AND is_active = TRUE', 
                       (session['user_id'],)).fetchone()
    conn.close()
    return dict(user) if user else None

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Get created user
        user = conn.execute('SELECT id, username, email FROM users WHERE id = ?', 
                           (user_id,)).fetchone()
        conn.close()
        
        # Create session
        session['user_id'] = user_id
        session['username'] = username
        session.permanent = True
        
        return jsonify({
            'message': 'Registration successful',
            'user': dict(user)
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        conn = get_db_connection()
        
        # Find user by username or email
        user = conn.execute('''
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) AND is_active = TRUE
        ''', (username_or_email, username_or_email.lower())).fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            # Create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    user = get_current_user()
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        })
    return jsonify({'error': 'User not found'}), 404

# Updated existing routes with authentication
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/entry', methods=['POST'])
@login_required
def create_entry():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Analyze sentiment
        sentiment_label, sentiment_score = analyze_sentiment(text)
        
        # Save to database with user_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO journal_entries (user_id, content, sentiment_label, sentiment_score, premium_unlocked)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], text, sentiment_label, sentiment_score, False))
        
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
@login_required
def get_entries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM journal_entries 
            WHERE user_id = ? 
            ORDER BY date_created DESC
        ''', (session['user_id'],))
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(entries)
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return jsonify({'error': 'Failed to fetch entries'}), 500

@app.route('/api/create-payment-link', methods=['POST'])
@login_required
def create_payment_link():
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return jsonify({'error': 'Entry ID is required'}), 400
        
        # Verify entry belongs to current user
        conn = get_db_connection()
        entry = conn.execute(
            'SELECT * FROM journal_entries WHERE id = ? AND user_id = ?', 
            (entry_id, session['user_id'])
        ).fetchone()
        conn.close()
        
        if not entry:
            return jsonify({'error': 'Entry not found'}), 404
        
        # Create payment link using IntaSend
        payment_data = {
            "amount": 50,  # KES 50
            "currency": "KES",
            "reference": f"moodflow_insight_{entry_id}_{session['user_id']}",
            "callback_url": f"{request.host_url}api/payment-webhook",
            "redirect_url": f"{request.host_url}?payment=success",
            "metadata": {
                "entry_id": str(entry_id),
                "user_id": str(session['user_id']),
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

@app.route('/api/generate-insight', methods=['POST'])
@login_required
def generate_insight():
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return jsonify({'error': 'Entry ID is required'}), 400
        
        # Get the entry and verify ownership
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM journal_entries 
            WHERE id = ? AND user_id = ?
        ''', (entry_id, session['user_id']))
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
            WHERE id = ? AND user_id = ?
        ''', (insight, entry_id, session['user_id']))
        conn.commit()
        conn.close()
        
        return jsonify({'insight': insight})
    
    except Exception as e:
        print(f"Insight generation error: {e}")
        return jsonify({'error': 'Failed to generate insight'}), 500

# Keep existing helper functions
def analyze_sentiment(text):
    """Analyze sentiment using Hugging Face API"""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        response = requests.post(api_url, headers=headers, json={"inputs": text})
        result = response.json()
        
        if response.status_code == 200 and result:
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

@app.route('/api/payment-webhook', methods=['POST'])
def payment_webhook():
    try:
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-IntaSend-Signature', '')
        
        if not verify_intasend_signature(payload, signature, INTASEND_SECRET_KEY):
            return jsonify({'error': 'Invalid signature'}), 401
        
        webhook_data = request.get_json()
        
        if webhook_data.get('state') == 'COMPLETE':
            metadata = webhook_data.get('metadata', {})
            entry_id = metadata.get('entry_id')
            user_id = metadata.get('user_id')
            
            if entry_id and user_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE journal_entries 
                    SET premium_unlocked = TRUE 
                    WHERE id = ? AND user_id = ?
                ''', (entry_id, user_id))
                conn.commit()
                conn.close()
                
                print(f"Premium unlocked for entry {entry_id}, user {user_id}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Configure session timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)  # Session lasts 7 days

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)