"""
Flask Backend API with MongoDB for Stress Detection System
============================================================
REST API endpoints with MongoDB database for:
- User authentication
- Stress prediction
- Recommendations
- Mood journaling
- Reports
- Chatbot

MongoDB Connection:
- Make sure MongoDB is running locally on port 27017
- Or update MONGO_URI with your MongoDB Atlas connection string
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Gemini AI for Chatbot
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠ google-generativeai not installed. Chatbot will use fallback responses.")

app = Flask(__name__)
CORS(app)

# ============================================
# MONGODB CONNECTION - PUT YOUR URL HERE!
# ============================================

# ⬇️⬇️⬇️ CHANGE THIS LINE WITH YOUR MONGODB URL ⬇️⬇️⬇️

# Option 1: Local MongoDB (if MongoDB is installed locally)
# MONGO_URI = "mongodb://localhost:27017/"

# Option 2: MongoDB Atlas (Cloud) - RECOMMENDED
# Replace with your connection string from MongoDB Atlas:
MONGO_URI = "mongodb+srv://zalakdoshi:zalakdoshi@cluster0.ghwqzyz.mongodb.net/"

# Example:
# MONGO_URI = "mongodb+srv://zalak:mypassword123@cluster0.abc123.mongodb.net/"

# ⬆️⬆️⬆️ CHANGE THE ABOVE LINE ⬆️⬆️⬆️

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client['stress_detection_db']
    
    # Collections
    users_collection = db['users']
    stress_history_collection = db['stress_history']
    mood_journal_collection = db['mood_journal']
    
    # Create indexes
    users_collection.create_index('email', unique=True)
    stress_history_collection.create_index('user_id')
    mood_journal_collection.create_index('user_id')
    
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")

# ============================================
# LOAD ML MODEL
# ============================================

MODEL_PATH = 'stress_model.pkl'
model_data = None

def load_model():
    global model_data
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)

try:
    load_model()
except:
    pass

# ============================================
# HELPER FUNCTIONS
# ============================================

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc

def time_to_minutes(t):
    """Convert time string (e.g., '7:00 AM') to minutes since midnight"""
    if pd.isnull(t) or t is None:
        return 420  # Default to 7:00 AM (420 minutes)
    try:
        x = pd.to_datetime(t)
        return x.hour * 60 + x.minute
    except:
        return 420

def preprocess_input(data):
    """Preprocess user input for prediction using OneHotEncoder (PROJECTML.ipynb approach)"""
    if model_data is None:
        return None
    
    # Extract preprocessing objects from model
    ohe = model_data.get('onehot_encoder')
    scaler = model_data.get('scaler')
    cat_cols = model_data.get('cat_cols', ['Gender', 'Occupation', 'Marital_Status', 
                                            'Smoking_Habit', 'Meditation_Practice', 'Exercise_Type'])
    numeric_cols = model_data.get('numeric_cols', ['Age', 'Sleep_Duration', 'Sleep_Quality', 
                                                    'Physical_Activity', 'Screen_Time', 'Caffeine_Intake', 
                                                    'Alcohol_Intake', 'Work_Hours', 'Travel_Time', 
                                                    'Social_Interactions', 'Blood_Pressure', 
                                                    'Cholesterol_Level', 'Blood_Sugar_Level',
                                                    'Wake_Up_Time', 'Bed_Time'])
    
    # Create DataFrame from input
    df = pd.DataFrame([data])
    
    # Convert time columns to minutes
    time_cols = ['Wake_Up_Time', 'Bed_Time']
    for col in time_cols:
        if col in df.columns:
            df[col] = df[col].apply(time_to_minutes)
    
    # Apply OneHotEncoder to categorical columns
    if ohe is not None and all(col in df.columns for col in cat_cols):
        cat_data = df[cat_cols]
        encoded_data = ohe.transform(cat_data)
        encoded_cols = ohe.get_feature_names_out(cat_cols)
        df_encoded = pd.DataFrame(encoded_data, columns=encoded_cols, index=df.index)
        df = df.drop(columns=cat_cols)
        df = pd.concat([df, df_encoded], axis=1)
    
    # Scale numerical columns
    existing_numeric_cols = [col for col in numeric_cols if col in df.columns]
    if scaler is not None and len(existing_numeric_cols) > 0:
        df[existing_numeric_cols] = scaler.transform(df[existing_numeric_cols])
    
    # Drop the target column if it exists
    if 'Stress_Detection' in df.columns:
        df = df.drop('Stress_Detection', axis=1)
    
    return df.values

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, email and password are required'}), 400
    
    # Check if email exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user document
    user_doc = {
        'user_id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'password': generate_password_hash(data['password']),
        'created_at': datetime.now()
    }
    
    # Insert into MongoDB
    result = users_collection.insert_one(user_doc)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user_doc['user_id'],
        'name': data['name']
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user in MongoDB
    user = users_collection.find_one({'email': data['email']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user['user_id'],
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
        processed_input = preprocess_input(data)
        
        if processed_input is None:
            return jsonify({'error': 'Error processing input'}), 400
        
        prediction = model_data['model'].predict(processed_input)[0]
        
        probabilities = None
        if hasattr(model_data['model'], 'predict_proba'):
            proba = model_data['model'].predict_proba(processed_input)[0]
            probabilities = {
                'High': round(proba[0] * 100, 2),
                'Low': round(proba[1] * 100, 2),
                'Medium': round(proba[2] * 100, 2)
            }
        
        stress_level = model_data['label_encoders']['Stress_Detection'].inverse_transform([prediction])[0]
        
        # Save to MongoDB
        if user_id:
            stress_doc = {
                'user_id': user_id,
                'stress_level': stress_level,
                'input_data': data,
                'prediction_date': datetime.now()
            }
            stress_history_collection.insert_one(stress_doc)
        
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
    
    if data.get('Sleep_Duration', 8) < 6:
        triggers.append({'factor': 'Sleep Duration', 'impact': 'High', 'recommendation': 'Aim for 7-8 hours of sleep'})
    
    if data.get('Work_Hours', 8) > 9:
        triggers.append({'factor': 'Work Hours', 'impact': 'High', 'recommendation': 'Consider work-life balance'})
    
    if data.get('Screen_Time', 4) > 6:
        triggers.append({'factor': 'Screen Time', 'impact': 'Medium', 'recommendation': 'Reduce screen exposure'})
    
    if data.get('Physical_Activity', 'Moderate') in ['None', 'Low', '1']:
        triggers.append({'factor': 'Physical Activity', 'impact': 'High', 'recommendation': 'Exercise at least 30 mins daily'})
    
    if data.get('Meditation_Practice', 'Yes') == 'No':
        triggers.append({'factor': 'Meditation', 'impact': 'Medium', 'recommendation': 'Start with 10 mins meditation daily'})
    
    if data.get('Caffeine_Intake', 'Low') in ['Moderate', 'High', '2', '3']:
        triggers.append({'factor': 'Caffeine Intake', 'impact': 'Medium', 'recommendation': 'Limit caffeine after 2 PM'})
    
    if data.get('Social_Interactions', 'Moderate') in ['Low', '1', '2']:
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
    
    # Get user's stress history from MongoDB
    history = list(stress_history_collection.find(
        {'user_id': user_id}
    ).sort('prediction_date', -1).limit(10))
    
    if not history:
        return jsonify({
            'forecast': 'Insufficient data',
            'message': 'Need more stress assessments for accurate forecasting'
        }), 200
    
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
    
    # Create journal document
    journal_doc = {
        'user_id': data['user_id'],
        'mood': data['mood'],
        'notes': data.get('notes', ''),
        'entry_date': datetime.now()
    }
    
    # Insert into MongoDB
    result = mood_journal_collection.insert_one(journal_doc)
    
    return jsonify({
        'message': 'Journal entry added',
        'entry_id': str(result.inserted_id)
    }), 201

@app.route('/api/journal/<user_id>', methods=['GET'])
def get_journal_entries(user_id):
    """Get user's mood journal entries"""
    entries = list(mood_journal_collection.find(
        {'user_id': user_id}
    ).sort('entry_date', -1).limit(30))
    
    # Convert to JSON serializable format
    for entry in entries:
        entry['id'] = str(entry['_id'])
        entry['entry_date'] = entry['entry_date'].isoformat()
        del entry['_id']
    
    return jsonify({
        'entries': entries,
        'count': len(entries)
    }), 200

# ============================================
# REPORTS ENDPOINTS
# ============================================

@app.route('/api/reports/weekly/<user_id>', methods=['GET'])
def weekly_report(user_id):
    """Generate weekly stress report"""
    week_ago = datetime.now() - timedelta(days=7)
    
    history = list(stress_history_collection.find({
        'user_id': user_id,
        'prediction_date': {'$gte': week_ago}
    }).sort('prediction_date', 1))
    
    if not history:
        return jsonify({
            'message': 'No data available for this week',
            'data': []
        }), 200
    
    counts = {'Low': 0, 'Medium': 0, 'High': 0}
    for h in history:
        counts[h['stress_level']] = counts.get(h['stress_level'], 0) + 1
    
    total = len(history)
    percentages = {k: round(v/total*100, 1) for k, v in counts.items()}
    
    # Convert for JSON
    data = []
    for h in history:
        data.append({
            'stress_level': h['stress_level'],
            'prediction_date': h['prediction_date'].isoformat()
        })
    
    return jsonify({
        'period': 'Weekly',
        'total_assessments': total,
        'distribution': counts,
        'percentages': percentages,
        'dominant_level': max(counts, key=counts.get),
        'data': data
    }), 200

@app.route('/api/reports/monthly/<user_id>', methods=['GET'])
def monthly_report(user_id):
    """Generate monthly stress report"""
    month_ago = datetime.now() - timedelta(days=30)
    
    history = list(stress_history_collection.find({
        'user_id': user_id,
        'prediction_date': {'$gte': month_ago}
    }).sort('prediction_date', 1))
    
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
    
    data = []
    for h in history:
        data.append({
            'stress_level': h['stress_level'],
            'prediction_date': h['prediction_date'].isoformat()
        })
    
    return jsonify({
        'period': 'Monthly',
        'total_assessments': total,
        'distribution': counts,
        'percentages': percentages,
        'dominant_level': max(counts, key=counts.get),
        'data': data
    }), 200

@app.route('/api/reports/before-after/<user_id>', methods=['GET'])
def before_after_report(user_id):
    """Compare first assessment vs latest for progress tracking"""
    # Get first assessment
    first = stress_history_collection.find_one(
        {'user_id': user_id},
        sort=[('prediction_date', 1)]
    )
    
    # Get latest assessment
    latest = stress_history_collection.find_one(
        {'user_id': user_id},
        sort=[('prediction_date', -1)]
    )
    
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
            'date': first['prediction_date'].isoformat()
        },
        'after': {
            'level': latest['stress_level'],
            'date': latest['prediction_date'].isoformat()
        },
        'improvement': improvement,
        'message': message
    }), 200

# ============================================
# CHATBOT ENDPOINT (Dynamic AI-Powered)
# ============================================

# Gemini API Key
GEMINI_API_KEY = "AIzaSyAg5ZsWY9U-q80YnSujad26Iq81s5KE_Jg"

gemini_model = None

def init_gemini():
    """Initialize Gemini AI model"""
    global gemini_model
    if not GEMINI_AVAILABLE:
        print("⚠ Gemini library not available - using fallback responses")
        return False
    
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            # Test the model with a simple prompt
            test_response = gemini_model.generate_content("Hello")
            if test_response:
                print("✓ Gemini AI initialized and tested successfully!")
                return True
        except Exception as e:
            print(f"✗ Gemini AI initialization failed: {e}")
            return False
    else:
        print("⚠ Gemini API key not set")
    return False

# Try to initialize Gemini on startup
print("Initializing Gemini AI...")
init_gemini()

# Fallback responses when AI is not available
FALLBACK_RESPONSES = {
    'stressed': "I understand you're feeling stressed. Try taking a few deep breaths - inhale for 4 seconds, hold for 4, exhale for 6. This activates your parasympathetic nervous system and helps calm you down.",
    'anxious': "Anxiety can be challenging. Try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste. This helps bring you back to the present moment.",
    'tired': "Being tired can affect everything. Ensure you're getting 7-8 hours of quality sleep. Avoid screens 1 hour before bed, keep your room cool, and try a relaxing bedtime routine.",
    'help': "I'm here to help with stress management! I can assist with: breathing exercises, meditation guidance, sleep tips, work-life balance advice, and emotional support. What would you like to explore?",
    'breathing': "Let's do a calming breath together: Breathe in slowly through your nose for 4 seconds... Hold for 7 seconds... Exhale slowly through your mouth for 8 seconds. Repeat this 4 times.",
    'sleep': "For better sleep: 1) Stick to a consistent sleep schedule, 2) Avoid caffeine after 2pm, 3) Keep your bedroom dark and cool, 4) Try a relaxation routine before bed, 5) Limit screen time before sleep.",
    'work': "Work stress is very common. Try these strategies: 1) Take regular breaks every 90 minutes, 2) Prioritize your tasks, 3) Learn to say no to overcommitment, 4) Create boundaries between work and personal time.",
    'relax': "To deeply relax, try Progressive Muscle Relaxation: Starting from your toes, tense each muscle group for 5 seconds, then release. Move slowly up through your body to your head. This releases physical tension.",
    'meditation': "A simple meditation: Sit comfortably, close your eyes. Focus on your breath - notice the sensation of air entering and leaving. When thoughts arise, gently acknowledge them and return focus to your breath. Start with 5 minutes.",
    'default': "I'm here to support you with stress management. Whether you're feeling anxious, overwhelmed, or just need someone to talk to, I'm here. How are you feeling right now?"
}

# System prompt for Gemini to act as a stress support assistant
STRESS_SUPPORT_PROMPT = """You are a compassionate, professional AI stress management assistant for a stress detection and wellness application. Your role is to:

1. EMPATHY FIRST: Always acknowledge the user's feelings with empathy and validation
2. PROVIDE PRACTICAL ADVICE: Offer evidence-based stress management techniques
3. BE CONVERSATIONAL: Keep responses warm, friendly, and natural (not robotic)
4. STAY FOCUSED: Keep responses relevant to stress, mental wellness, relaxation, and emotional support
5. BE CONCISE: Keep responses helpful but not overwhelming (2-4 paragraphs max)
6. USE EMOJIS SPARINGLY: Add 1-2 relevant emojis to make responses friendly

Topics you can help with:
- Stress management techniques
- Breathing exercises (4-7-8 technique, box breathing, etc.)
- Meditation and mindfulness guidance
- Sleep hygiene tips
- Work-life balance advice
- Anxiety management
- Relaxation techniques (progressive muscle relaxation, grounding, etc.)
- Emotional support and active listening

IMPORTANT: Never diagnose conditions or replace professional mental health care. If someone seems in crisis, gently encourage them to seek professional help.

Respond to the following message from the user:"""

@app.route('/api/chat', methods=['POST'])
def chatbot():
    """AI-Powered Chatbot for stress support"""
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({
            'response': "I'm here to listen. How are you feeling today?",
            'timestamp': datetime.now().isoformat(),
            'ai_powered': False
        }), 200
    
    # Try Gemini AI first
    if gemini_model:
        try:
            full_prompt = f"{STRESS_SUPPORT_PROMPT}\n\nUser: {message}"
            response = gemini_model.generate_content(full_prompt)
            
            return jsonify({
                'response': response.text,
                'timestamp': datetime.now().isoformat(),
                'ai_powered': True
            }), 200
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fall through to fallback
    
    # Fallback: Use keyword-based responses
    message_lower = message.lower()
    response_text = FALLBACK_RESPONSES['default']
    
    for keyword, reply in FALLBACK_RESPONSES.items():
        if keyword in message_lower:
            response_text = reply
            break
    
    return jsonify({
        'response': response_text,
        'timestamp': datetime.now().isoformat(),
        'ai_powered': False,
        'note': 'Using fallback responses. Add Gemini API key for AI-powered chat.'
    }), 200

# ============================================
# STRESS HISTORY ENDPOINT
# ============================================

@app.route('/api/history/<user_id>', methods=['GET'])
def get_stress_history(user_id):
    """Get user's stress prediction history"""
    history = list(stress_history_collection.find(
        {'user_id': user_id}
    ).sort('prediction_date', -1))
    
    # Convert for JSON
    for h in history:
        h['id'] = str(h['_id'])
        h['prediction_date'] = h['prediction_date'].isoformat()
        del h['_id']
        if 'input_data' in h:
            del h['input_data']  # Remove large input data from response
    
    return jsonify({
        'history': history,
        'count': len(history)
    }), 200

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        mongo_status = 'connected'
    except:
        mongo_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_data is not None,
        'mongodb': mongo_status,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 45)
    print("  STRESS DETECTION BACKEND (MongoDB)")
    print("=" * 45)
    print("\n  Server: http://localhost:5000")
    print("=" * 45 + "\n")
    
    # Run with minimal output
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(debug=False, port=5000)
