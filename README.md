# 🧘 AI-Based Stress Detection & Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb)
![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-4285F4?style=flat-square&logo=google)

**A comprehensive AI-powered web application for detecting, analyzing, and managing stress levels using Machine Learning and Generative AI.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Tech Stack](#-tech-stack) • [API Reference](#-api-endpoints)

</div>

---

## 🌟 Overview

This Stress Detection & Management System uses **Machine Learning** to predict stress levels based on lifestyle factors like sleep, work hours, exercise, and more. It provides personalized recommendations, AI-powered chat support, mood journaling, and comprehensive reports to help users understand and manage their stress effectively.

## ✨ Features

### Core Features
- 🔐 **User Authentication** - Secure login/registration with password hashing
- 🧠 **ML Stress Prediction** - Predicts Low/Medium/High stress using Random Forest
- 📊 **Trigger Analysis** - Identifies key stress factors from your lifestyle
- 📈 **Stress Forecasting** - Predicts future stress trends based on history

### AI-Powered Features
- 🤖 **Gemini AI Chatbot** - Dynamic, intelligent stress support conversations
- 💡 **Smart Recommendations** - Dynamic, editable recommendations per stress level
- 🚨 **Emergency Relief** - S.T.O.P. technique for immediate stress relief

### Tracking & Reports
- 📝 **Mood Journaling** - Track daily moods and feelings
- 📅 **Weekly/Monthly Reports** - Visualize stress patterns over time
- 📉 **Before/After Analysis** - Track your improvement journey

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React.js 18, Axios, Modern CSS |
| **Backend** | Flask 3.0, Python 3.9+ |
| **Database** | MongoDB Atlas (Cloud) / SQLite (Local) |
| **ML Model** | scikit-learn (Random Forest, SVM, LR) |
| **AI Chatbot** | Google Gemini 2.5 Flash |
| **Authentication** | Werkzeug Security (Password Hashing) |

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB Atlas account (free) or local MongoDB
- Google Gemini API key (free)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stress-detection-system.git
cd stress-detection-system
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend/src

# Install Python dependencies
pip install -r requirements.txt

# Train the ML model (run once)
python stress_model.py

# Configure MongoDB and Gemini API keys in app_mongodb.py
# MONGO_URI = "your-mongodb-uri"
# GEMINI_API_KEY = "your-gemini-api-key"

# Run the server
python app_mongodb.py
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000

## 🗄️ Database Setup

### MongoDB Atlas (Recommended)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free M0 tier)
3. Create a database user with password
4. Whitelist your IP (or 0.0.0.0/0 for development)
5. Get connection string and update `app_mongodb.py`:

```python
MONGO_URI = "mongodb+srv://<username>:<password>@cluster.xxxxx.mongodb.net/"
```

### Gemini AI Setup (For Chatbot)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a free API key
3. Update `app_mongodb.py`:

```python
GEMINI_API_KEY = "your-api-key-here"
```

## 📁 Project Structure

```
stress_management_sys/
├── backend/
│   └── src/
│       ├── app_mongodb.py       # Flask API (MongoDB + Gemini AI)
│       ├── app.py               # Flask API (SQLite version)
│       ├── stress_model.py      # ML model training script
│       ├── stress_model.pkl     # Trained ML model
│       ├── stress_detection_data.csv
│       └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React app
│   │   ├── App.css             # Global styles
│   │   ├── components/
│   │   │   └── Navbar.js
│   │   └── pages/
│   │       ├── Login.js
│   │       ├── Register.js
│   │       ├── Dashboard.js    # Main dashboard
│   │       ├── StressForm.js   # Stress assessment form
│   │       ├── Recommendations.js  # Dynamic recommendations
│   │       ├── Journal.js      # Mood journaling
│   │       ├── Reports.js      # Weekly/Monthly reports
│   │       └── Chatbot.js      # AI-powered chatbot
│   └── package.json
└── README.md
```

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login user |

### Stress Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Predict stress level (ML) |
| POST | `/api/analyze-triggers` | Analyze stress triggers |
| POST | `/api/forecast` | Forecast stress trends |
| GET | `/api/history/:userId` | Get stress history |

### Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recommendations/:level` | Get recommendations by level |
| POST | `/api/recommendations` | Add new recommendation |
| PUT | `/api/recommendations/:id` | Update recommendation |
| DELETE | `/api/recommendations/:id` | Delete recommendation |
| GET | `/api/emergency-tips` | Emergency relief tips |

### Journaling & Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/journal` | Add journal entry |
| GET | `/api/journal/:userId` | Get journal entries |
| GET | `/api/reports/weekly/:userId` | Weekly stress report |
| GET | `/api/reports/monthly/:userId` | Monthly stress report |
| GET | `/api/reports/before-after/:userId` | Progress comparison |

### AI Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | AI-powered chat (Gemini) |

## 🧠 Machine Learning Model

| Aspect | Details |
|--------|---------|
| **Dataset** | 774 samples, 22 features |
| **Algorithms Tested** | Random Forest, SVM, Logistic Regression |
| **Best Model** | Random Forest |
| **Accuracy** | 72.9% |
| **Features** | Age, Gender, Occupation, Sleep Duration, Sleep Quality, Work Hours, Screen Time, Exercise, Caffeine, Alcohol, Smoking, Social Interactions, Meditation, Blood Pressure, Cholesterol, Blood Sugar |
| **Target** | Stress Level (Low / Medium / High) |

## 📸 Screenshots

*Add your application screenshots here*

| Dashboard | Stress Form | AI Chatbot |
|-----------|-------------|------------|
| ![Dashboard](screenshots/dashboard.png) | ![Form](screenshots/form.png) | ![Chatbot](screenshots/chatbot.png) |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

## 📝 License

This project is developed for educational purposes (B.Tech Final/Mini Project).

---

<div align="center">

⭐ **Star this repo if you find it helpful!** ⭐

Made with ❤️ for stress-free living

</div>
