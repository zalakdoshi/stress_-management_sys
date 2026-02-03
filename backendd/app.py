"""
Flask Backend API for Stress Detection System
==============================================
REST API endpoints for:
- User authentication
- Stress prediction
- Recommendations
- Mood journaling
- Reports
- Chatbot
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
CORS(app)

# ============================================
# DATABASE SETUP
# ============================================

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('stress_app.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    
    # Stress history table
    c.execute('''CREATE TABLE IF NOT EXISTS stress_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        stress_level TEXT NOT NULL,
        input_data TEXT NOT NULL,
        prediction_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Mood journal table
    c.execute('''CREATE TABLE IF NOT EXISTS mood_journal (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        mood TEXT NOT NULL,
        notes TEXT,
        entry_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ============================================
# LOAD ML MODEL
# ============================================

MODEL_PATH = 'stress_model.pkl'
model_data = None

def load_model():
    global model_data
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)
        print("✓ ML Model loaded successfully!")
    else:
        print("⚠ ML Model not found. Please train the model first.")

# Try to load model on startup
try:
    load_model()
except Exception as e:
    print(f"Error loading model: {e}")

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_db():
    conn = sqlite3.connect('stress_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def preprocess_input(data):
    """Preprocess user input for prediction"""
    if model_data is None:
        return None
    
    # Define feature order
    features = ['Age', 'Gender', 'Occupation', 'Marital_Status', 'Sleep_Duration',
                'Sleep_Quality', 'Wake_Up_Time', 'Bed_Time', 'Physical_Activity',
                'Screen_Time', 'Caffeine_Intake', 'Alcohol_Intake', 'Smoking_Habit',
                'Work_Hours', 'Travel_Time', 'Social_Interactions', 'Meditation_Practice',
                'Exercise_Type', 'Blood_Pressure', 'Cholesterol_Level', 'Blood_Sugar_Level']
    
    # Create DataFrame
    df = pd.DataFrame([data])
    
    # Encode categorical variables
    categorical_cols = ['Gender', 'Occupation', 'Marital_Status', 'Sleep_Quality',
                        'Wake_Up_Time', 'Bed_Time', 'Physical_Activity',
                        'Caffeine_Intake', 'Alcohol_Intake', 'Smoking_Habit',
                        'Social_Interactions', 'Meditation_Practice', 'Exercise_Type',
                        'Blood_Pressure', 'Cholesterol_Level', 'Blood_Sugar_Level']
    
    for col in categorical_cols:
        if col in model_data['label_encoders']:
            le = model_data['label_encoders'][col]
            if data[col] in le.classes_:
                df[col] = le.transform([data[col]])[0]
            else:
                df[col] = 0  # Default for unknown categories
    
    # Scale numerical features
    numerical_cols = ['Age', 'Sleep_Duration', 'Screen_Time', 'Work_Hours', 'Travel_Time']
    df[numerical_cols] = model_data['scaler'].transform(df[numerical_cols])
    
    return df[features].values

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, email and password are required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if email exists
    c.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(data['password'])
    
    c.execute('''INSERT INTO users (id, name, email, password, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, data['name'], data['email'], hashed_password, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user_id,
        'name': data['name']
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
    user = c.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user['id'],
        'name': user['name'],
        'email': user['email']
    }), 200

# ============================================
# STRESS PREDICTION ENDPOINTS
# ============================================

@app.route('/api/predict', methods=['POST'])
def predict_stress():
    """Predict stress level based on user input"""
    if model_data is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.json
    user_id = data.get('user_id')
    
    try:
        # Preprocess input
        processed_input = preprocess_input(data)
        
        if processed_input is None:
            return jsonify({'error': 'Error processing input'}), 400
        
        # Make prediction
        prediction = model_data['model'].predict(processed_input)[0]
        
        # Get probability if available
        probabilities = None
        if hasattr(model_data['model'], 'predict_proba'):
            proba = model_data['model'].predict_proba(processed_input)[0]
            probabilities = {
                'High': round(proba[0] * 100, 2),
                'Low': round(proba[1] * 100, 2),
                'Medium': round(proba[2] * 100, 2)
            }
        
        # Decode prediction
        stress_level = model_data['label_encoders']['Stress_Detection'].inverse_transform([prediction])[0]
        
        # Save to database if user_id provided
        if user_id:
            conn = get_db()
            c = conn.cursor()
            c.execute('''INSERT INTO stress_history (id, user_id, stress_level, input_data, prediction_date)
                        VALUES (?, ?, ?, ?, ?)''',
                      (str(uuid.uuid4()), user_id, stress_level, json.dumps(data), datetime.now().isoformat()))
            conn.commit()
            conn.close()
        
        return jsonify({
            'stress_level': stress_level,
            'probabilities': probabilities,
            'message': f'Your stress level is {stress_level}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-triggers', methods=['POST'])
def analyze_triggers():
    """Analyze stress triggers from user data"""
    data = request.json
    
    triggers = []
    
    # Analyze based on input data
    if data.get('Sleep_Duration', 8) < 6:
        triggers.append({'factor': 'Sleep Duration', 'impact': 'High', 'recommendation': 'Aim for 7-8 hours of sleep'})
    
    if data.get('Work_Hours', 8) > 9:
        triggers.append({'factor': 'Work Hours', 'impact': 'High', 'recommendation': 'Consider work-life balance'})
    
    if data.get('Screen_Time', 4) > 6:
        triggers.append({'factor': 'Screen Time', 'impact': 'Medium', 'recommendation': 'Reduce screen exposure'})
    
    if data.get('Physical_Activity', 'Moderate') == 'None' or data.get('Physical_Activity') == 'Low':
        triggers.append({'factor': 'Physical Activity', 'impact': 'High', 'recommendation': 'Exercise at least 30 mins daily'})
    
    if data.get('Meditation_Practice', 'Yes') == 'No':
        triggers.append({'factor': 'Meditation', 'impact': 'Medium', 'recommendation': 'Start with 10 mins meditation daily'})
    
    if data.get('Caffeine_Intake', 'Low') in ['Moderate', 'High']:
        triggers.append({'factor': 'Caffeine Intake', 'impact': 'Medium', 'recommendation': 'Limit caffeine after 2 PM'})
    
    if data.get('Social_Interactions', 'Moderate') == 'Low':
        triggers.append({'factor': 'Social Interactions', 'impact': 'Medium', 'recommendation': 'Connect with friends/family'})
    
    return jsonify({
        'triggers': triggers,
        'total_triggers': len(triggers)
    }), 200

@app.route('/api/forecast', methods=['POST'])
def forecast_stress():
    """Forecast future stress based on patterns"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # Get user's stress history
    c.execute('''SELECT stress_level, prediction_date FROM stress_history 
                 WHERE user_id = ? ORDER BY prediction_date DESC LIMIT 10''', (user_id,))
    history = c.fetchall()
    conn.close()
    
    if not history:
        return jsonify({
            'forecast': 'Insufficient data',
            'message': 'Need more stress assessments for accurate forecasting'
        }), 200
    
    # Simple forecasting based on recent trends
    stress_scores = {'Low': 1, 'Medium': 2, 'High': 3}
    scores = [stress_scores.get(h['stress_level'], 2) for h in history]
    avg_score = sum(scores) / len(scores)
    trend = scores[0] - scores[-1] if len(scores) > 1 else 0
    
    if trend > 0:
        forecast = 'Increasing'
        message = 'Your stress levels are showing an upward trend. Take preventive measures.'
    elif trend < 0:
        forecast = 'Decreasing'
        message = 'Great! Your stress levels are improving. Keep up the good work!'
    else:
        forecast = 'Stable'
        message = 'Your stress levels are stable. Continue your current routine.'
    
    return jsonify({
        'forecast': forecast,
        'average_level': 'Low' if avg_score < 1.5 else 'Medium' if avg_score < 2.5 else 'High',
        'message': message,
        'data_points': len(history)
    }), 200

# ============================================
# RECOMMENDATIONS ENDPOINTS
# ============================================

RECOMMENDATIONS = {
    'Low': [
        {'title': 'Maintain Your Routine', 'description': 'Continue your current healthy habits', 'icon': '✅'},
        {'title': 'Daily Meditation', 'description': '10-15 minutes of mindfulness', 'icon': '🧘'},
        {'title': 'Stay Active', 'description': 'Regular exercise keeps stress away', 'icon': '🏃'},
        {'title': 'Quality Sleep', 'description': 'Maintain 7-8 hours of sleep', 'icon': '😴'}
    ],
    'Medium': [
        {'title': 'Deep Breathing Exercises', 'description': 'Practice 4-7-8 breathing technique', 'icon': '🌬️'},
        {'title': 'Take Regular Breaks', 'description': 'Step away from work every 90 minutes', 'icon': '⏰'},
        {'title': 'Reduce Caffeine', 'description': 'Limit coffee intake after noon', 'icon': '☕'},
        {'title': 'Connect with Others', 'description': 'Talk to friends or family', 'icon': '👥'},
        {'title': 'Nature Walk', 'description': '20 minutes outdoors daily', 'icon': '🌳'},
        {'title': 'Journaling', 'description': 'Write down your thoughts', 'icon': '📝'}
    ],
    'High': [
        {'title': 'STOP & Breathe', 'description': 'Take 5 deep breaths right now', 'icon': '🛑'},
        {'title': 'Progressive Muscle Relaxation', 'description': 'Release tension from your body', 'icon': '💆'},
        {'title': 'Prioritize Sleep', 'description': 'Get at least 8 hours tonight', 'icon': '🛏️'},
        {'title': 'Limit Screen Time', 'description': 'Digital detox for 2 hours before bed', 'icon': '📱'},
        {'title': 'Talk to Someone', 'description': 'Share your feelings with a trusted person', 'icon': '💬'},
        {'title': 'Light Exercise', 'description': 'A short walk can help immensely', 'icon': '🚶'},
        {'title': 'Avoid Stimulants', 'description': 'No caffeine or alcohol today', 'icon': '🚫'},
        {'title': 'Listen to Calming Music', 'description': 'Relaxing sounds can reduce stress', 'icon': '🎵'}
    ]
}

@app.route('/api/recommendations/<stress_level>', methods=['GET'])
def get_recommendations(stress_level):
    """Get personalized stress management recommendations"""
    level = stress_level.capitalize()
    
    if level not in RECOMMENDATIONS:
        return jsonify({'error': 'Invalid stress level'}), 400
    
    return jsonify({
        'stress_level': level,
        'recommendations': RECOMMENDATIONS[level],
        'count': len(RECOMMENDATIONS[level])
    }), 200

@app.route('/api/emergency-tips', methods=['GET'])
def emergency_tips():
    """Get emergency stress relief tips"""
    tips = [
        {'step': 1, 'title': 'STOP', 'description': 'Stop whatever you are doing'},
        {'step': 2, 'title': 'BREATHE', 'description': 'Take 5 slow, deep breaths'},
        {'step': 3, 'title': 'OBSERVE', 'description': 'Notice your thoughts without judgment'},
        {'step': 4, 'title': 'PROCEED', 'description': 'Continue with awareness'},
        {'step': 5, 'title': 'GROUND', 'description': 'Name 5 things you can see, 4 you can touch, 3 you can hear'}
    ]
    
    return jsonify({
        'tips': tips,
        'message': 'Take your time. This feeling will pass.'
    }), 200

# ============================================
# MOOD JOURNAL ENDPOINTS
# ============================================

@app.route('/api/journal', methods=['POST'])
def add_journal_entry():
    """Add a mood journal entry"""
    data = request.json
    
    if not data.get('user_id') or not data.get('mood'):
        return jsonify({'error': 'User ID and mood are required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    entry_id = str(uuid.uuid4())
    c.execute('''INSERT INTO mood_journal (id, user_id, mood, notes, entry_date)
                 VALUES (?, ?, ?, ?, ?)''',
              (entry_id, data['user_id'], data['mood'], data.get('notes', ''), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Journal entry added',
        'entry_id': entry_id
    }), 201

@app.route('/api/journal/<user_id>', methods=['GET'])
def get_journal_entries(user_id):
    """Get user's mood journal entries"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM mood_journal WHERE user_id = ? 
                 ORDER BY entry_date DESC LIMIT 30''', (user_id,))
    entries = c.fetchall()
    conn.close()
    
    return jsonify({
        'entries': [dict(e) for e in entries],
        'count': len(entries)
    }), 200

# ============================================
# REPORTS ENDPOINTS
# ============================================

@app.route('/api/reports/weekly/<user_id>', methods=['GET'])
def weekly_report(user_id):
    """Generate weekly stress report"""
    conn = get_db()
    c = conn.cursor()
    
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    c.execute('''SELECT stress_level, prediction_date FROM stress_history 
                 WHERE user_id = ? AND prediction_date >= ?
                 ORDER BY prediction_date''', (user_id, week_ago))
    history = c.fetchall()
    conn.close()
    
    if not history:
        return jsonify({
            'message': 'No data available for this week',
            'data': []
        }), 200
    
    # Count stress levels
    counts = {'Low': 0, 'Medium': 0, 'High': 0}
    for h in history:
        counts[h['stress_level']] = counts.get(h['stress_level'], 0) + 1
    
    total = len(history)
    percentages = {k: round(v/total*100, 1) for k, v in counts.items()}
    
    return jsonify({
        'period': 'Weekly',
        'total_assessments': total,
        'distribution': counts,
        'percentages': percentages,
        'dominant_level': max(counts, key=counts.get),
        'data': [dict(h) for h in history]
    }), 200

@app.route('/api/reports/monthly/<user_id>', methods=['GET'])
def monthly_report(user_id):
    """Generate monthly stress report"""
    conn = get_db()
    c = conn.cursor()
    
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    c.execute('''SELECT stress_level, prediction_date FROM stress_history 
                 WHERE user_id = ? AND prediction_date >= ?
                 ORDER BY prediction_date''', (user_id, month_ago))
    history = c.fetchall()
    conn.close()
    
    if not history:
        return jsonify({
            'message': 'No data available for this month',
            'data': []
        }), 200
    
    counts = {'Low': 0, 'Medium': 0, 'High': 0}
    for h in history:
        counts[h['stress_level']] = counts.get(h['stress_level'], 0) + 1
    
    total = len(history)
    percentages = {k: round(v/total*100, 1) for k, v in counts.items()}
    
    return jsonify({
        'period': 'Monthly',
        'total_assessments': total,
        'distribution': counts,
        'percentages': percentages,
        'dominant_level': max(counts, key=counts.get),
        'data': [dict(h) for h in history]
    }), 200

@app.route('/api/reports/before-after/<user_id>', methods=['GET'])
def before_after_report(user_id):
    """Compare first assessment vs latest for progress tracking"""
    conn = get_db()
    c = conn.cursor()
    
    # Get first assessment
    c.execute('''SELECT stress_level, prediction_date FROM stress_history 
                 WHERE user_id = ? ORDER BY prediction_date ASC LIMIT 1''', (user_id,))
    first = c.fetchone()
    
    # Get latest assessment
    c.execute('''SELECT stress_level, prediction_date FROM stress_history 
                 WHERE user_id = ? ORDER BY prediction_date DESC LIMIT 1''', (user_id,))
    latest = c.fetchone()
    
    conn.close()
    
    if not first or not latest:
        return jsonify({
            'message': 'Insufficient data for comparison',
            'data': None
        }), 200
    
    stress_scores = {'Low': 1, 'Medium': 2, 'High': 3}
    first_score = stress_scores.get(first['stress_level'], 2)
    latest_score = stress_scores.get(latest['stress_level'], 2)
    
    if latest_score < first_score:
        improvement = 'Improved'
        message = '🎉 Great progress! Your stress levels have decreased.'
    elif latest_score > first_score:
        improvement = 'Declined'
        message = '⚠️ Your stress levels have increased. Consider following our recommendations.'
    else:
        improvement = 'Stable'
        message = 'Your stress levels remain stable.'
    
    return jsonify({
        'before': {
            'level': first['stress_level'],
            'date': first['prediction_date']
        },
        'after': {
            'level': latest['stress_level'],
            'date': latest['prediction_date']
        },
        'improvement': improvement,
        'message': message
    }), 200

# ============================================
# CHATBOT ENDPOINT
# ============================================

CHATBOT_RESPONSES = {
    'hello': "Hello! I'm here to help you manage stress. How are you feeling today?",
    'hi': "Hi there! How can I help you feel better today?",
    'stressed': "I understand you're feeling stressed. Take a deep breath. Would you like some relaxation techniques?",
    'anxious': "Anxiety can be tough. Try the 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s. Repeat 4 times.",
    'tired': "Rest is important. Are you getting enough sleep? Aim for 7-8 hours each night.",
    'help': "I can help with: stress tips, breathing exercises, sleep advice, or just chat. What do you need?",
    'breathing': "Try this: Breathe in slowly for 4 seconds, hold for 4, exhale for 6. Repeat 5 times.",
    'sleep': "For better sleep: avoid screens 1hr before bed, keep room cool, try lavender scent.",
    'exercise': "Even a 10-minute walk can reduce stress. Movement releases endorphins!",
    'work': "Work stress is common. Take breaks every 90 minutes and set boundaries between work and rest.",
    'relax': "To relax: try progressive muscle relaxation - tense then release each muscle group from toes to head.",
    'thank': "You're welcome! Remember, it's okay to ask for help. Take care of yourself! 💙",
    'bye': "Take care! Remember to be kind to yourself. Come back anytime you need support. 👋"
}

@app.route('/api/chat', methods=['POST'])
def chatbot():
    """AI Chatbot for stress support"""
    data = request.json
    message = data.get('message', '').lower()
    
    # Find matching response
    response = "I'm here to help with stress management. Tell me how you're feeling or ask about relaxation techniques."
    
    for keyword, reply in CHATBOT_RESPONSES.items():
        if keyword in message:
            response = reply
            break
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================
# STRESS HISTORY ENDPOINT
# ============================================

@app.route('/api/history/<user_id>', methods=['GET'])
def get_stress_history(user_id):
    """Get user's stress prediction history"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM stress_history WHERE user_id = ? 
                 ORDER BY prediction_date DESC''', (user_id,))
    history = c.fetchall()
    conn.close()
    
    return jsonify({
        'history': [dict(h) for h in history],
        'count': len(history)
    }), 200

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_data is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("   STRESS DETECTION API SERVER")
    print("=" * 50)
    print("\n✓ Starting Flask server...")
    print("✓ API available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/register        - Register user")
    print("  POST /api/login           - Login user")
    print("  POST /api/predict         - Predict stress")
    print("  POST /api/analyze-triggers- Analyze triggers")
    print("  POST /api/forecast        - Forecast stress")
    print("  GET  /api/recommendations - Get recommendations")
    print("  POST /api/journal         - Add journal entry")
    print("  GET  /api/journal/<id>    - Get journal entries")
    print("  GET  /api/reports/weekly  - Weekly report")
    print("  GET  /api/reports/monthly - Monthly report")
    print("  GET  /api/reports/before-after - Before/After comparison")
    print("  POST /api/chat            - Chatbot")
    print("=" * 50 + "\n")
    
    app.run(debug=True, port=5000)
