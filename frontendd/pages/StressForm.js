import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function StressForm() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    Age: '',
    Gender: 'Male',
    Occupation: 'Software Engineer',
    Marital_Status: 'Single',
    Sleep_Duration: '',
    Sleep_Quality: '4',
    Wake_Up_Time: '7:00 AM',
    Bed_Time: '10:00 PM',
    Physical_Activity: '2',
    Screen_Time: '',
    Caffeine_Intake: '1',
    Alcohol_Intake: '0',
    Smoking_Habit: 'No',
    Work_Hours: '',
    Travel_Time: '',
    Social_Interactions: '4',
    Meditation_Practice: 'No',
    Exercise_Type: 'Cardio',
    Blood_Pressure: '120',
    Cholesterol_Level: '180',
    Blood_Sugar_Level: '90'
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/predict`, {
        ...formData,
        user_id: user.user_id
      });
      setResult(response.data);
    } catch (err) {
      console.error('Prediction error:', err);
      alert('Error making prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getResultIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return '😊';
      case 'medium': return '😐';
      case 'high': return '😰';
      default: return '🤔';
    }
  };

  const occupations = [
    'Software Engineer', 'Teacher', 'Doctor', 'Nurse', 'Marketing Manager',
    'Data Scientist', 'Graphic Designer', 'Civil Engineer', 'Business Owner',
    'Architect', 'Lawyer', 'Accountant', 'Chef', 'Photographer', 'Driver',
    'Student', 'Freelancer', 'Other'
  ];

  const exerciseTypes = ['None', 'Cardio', 'Yoga', 'Strength Training', 'Pilates', 'Walking', 'Aerobics', 'Meditation'];

  if (result) {
    return (
      <div className="result-modal">
        <div className="result-card">
          <div className="result-icon">{getResultIcon(result.stress_level)}</div>
          <div className="result-title">Your Stress Level</div>
          <div className={`result-level ${result.stress_level.toLowerCase()}`}>
            {result.stress_level}
          </div>
          <p className="result-message">{result.message}</p>
          
          {result.probabilities && (
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '1rem' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: '#10b981', fontWeight: '600' }}>{result.probabilities.Low}%</div>
                  <div style={{ color: '#888', fontSize: '0.8rem' }}>Low</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: '#f59e0b', fontWeight: '600' }}>{result.probabilities.Medium}%</div>
                  <div style={{ color: '#888', fontSize: '0.8rem' }}>Medium</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: '#ef4444', fontWeight: '600' }}>{result.probabilities.High}%</div>
                  <div style={{ color: '#888', fontSize: '0.8rem' }}>High</div>
                </div>
              </div>
            </div>
          )}

          <div className="result-actions">
            <button className="btn btn-primary" onClick={() => navigate('/recommendations')}>
              Get Recommendations
            </button>
            <button className="btn btn-secondary" onClick={() => setResult(null)}>
              Take Another Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="stress-form-container">
      <div className="stress-form-header">
        <h1>🧠 Stress Assessment</h1>
        <p>Fill in your details to check your stress level</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Personal Information */}
        <div className="form-section">
          <h3>👤 Personal Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Age</label>
              <input type="number" name="Age" value={formData.Age} onChange={handleChange} min="18" max="80" required />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select name="Gender" value={formData.Gender} onChange={handleChange}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Occupation</label>
              <select name="Occupation" value={formData.Occupation} onChange={handleChange}>
                {occupations.map(occ => <option key={occ} value={occ}>{occ}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Marital Status</label>
              <select name="Marital_Status" value={formData.Marital_Status} onChange={handleChange}>
                <option value="Single">Single</option>
                <option value="Married">Married</option>
                <option value="Divorced">Divorced</option>
              </select>
            </div>
          </div>
        </div>

        {/* Sleep Patterns */}
        <div className="form-section">
          <h3>😴 Sleep Patterns</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Sleep Duration (hours)</label>
              <input type="number" name="Sleep_Duration" value={formData.Sleep_Duration} onChange={handleChange} min="3" max="12" step="0.5" required />
            </div>
            <div className="form-group">
              <label>Sleep Quality (1-5)</label>
              <select name="Sleep_Quality" value={formData.Sleep_Quality} onChange={handleChange}>
                <option value="1">1 - Very Poor</option>
                <option value="2">2 - Poor</option>
                <option value="3">3 - Average</option>
                <option value="4">4 - Good</option>
                <option value="5">5 - Excellent</option>
              </select>
            </div>
            <div className="form-group">
              <label>Wake Up Time</label>
              <select name="Wake_Up_Time" value={formData.Wake_Up_Time} onChange={handleChange}>
                <option value="5:00 AM">5:00 AM</option>
                <option value="5:30 AM">5:30 AM</option>
                <option value="6:00 AM">6:00 AM</option>
                <option value="6:30 AM">6:30 AM</option>
                <option value="7:00 AM">7:00 AM</option>
                <option value="7:30 AM">7:30 AM</option>
                <option value="8:00 AM">8:00 AM</option>
                <option value="8:30 AM">8:30 AM</option>
                <option value="9:00 AM">9:00 AM</option>
              </select>
            </div>
            <div className="form-group">
              <label>Bed Time</label>
              <select name="Bed_Time" value={formData.Bed_Time} onChange={handleChange}>
                <option value="9:00 PM">9:00 PM</option>
                <option value="9:30 PM">9:30 PM</option>
                <option value="10:00 PM">10:00 PM</option>
                <option value="10:30 PM">10:30 PM</option>
                <option value="11:00 PM">11:00 PM</option>
                <option value="11:30 PM">11:30 PM</option>
                <option value="12:00 AM">12:00 AM</option>
                <option value="12:30 AM">12:30 AM</option>
                <option value="1:00 AM">1:00 AM</option>
              </select>
            </div>
          </div>
        </div>

        {/* Lifestyle */}
        <div className="form-section">
          <h3>🏃 Lifestyle & Habits</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Physical Activity Level (1-5)</label>
              <select name="Physical_Activity" value={formData.Physical_Activity} onChange={handleChange}>
                <option value="1">1 - None</option>
                <option value="2">2 - Low</option>
                <option value="3">3 - Moderate</option>
                <option value="4">4 - High</option>
                <option value="5">5 - Very High</option>
              </select>
            </div>
            <div className="form-group">
              <label>Screen Time (hours/day)</label>
              <input type="number" name="Screen_Time" value={formData.Screen_Time} onChange={handleChange} min="0" max="16" required />
            </div>
            <div className="form-group">
              <label>Exercise Type</label>
              <select name="Exercise_Type" value={formData.Exercise_Type} onChange={handleChange}>
                {exerciseTypes.map(ex => <option key={ex} value={ex}>{ex}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Meditation Practice</label>
              <select name="Meditation_Practice" value={formData.Meditation_Practice} onChange={handleChange}>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Caffeine Intake (cups/day)</label>
              <select name="Caffeine_Intake" value={formData.Caffeine_Intake} onChange={handleChange}>
                <option value="0">0 - None</option>
                <option value="1">1 cup</option>
                <option value="2">2 cups</option>
                <option value="3">3+ cups</option>
              </select>
            </div>
            <div className="form-group">
              <label>Alcohol Intake</label>
              <select name="Alcohol_Intake" value={formData.Alcohol_Intake} onChange={handleChange}>
                <option value="0">None</option>
                <option value="1">Occasional</option>
                <option value="2">Regular</option>
              </select>
            </div>
            <div className="form-group">
              <label>Smoking Habit</label>
              <select name="Smoking_Habit" value={formData.Smoking_Habit} onChange={handleChange}>
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
            </div>
            <div className="form-group">
              <label>Social Interactions (1-5)</label>
              <select name="Social_Interactions" value={formData.Social_Interactions} onChange={handleChange}>
                <option value="1">1 - Very Low</option>
                <option value="2">2 - Low</option>
                <option value="3">3 - Moderate</option>
                <option value="4">4 - Good</option>
                <option value="5">5 - Very High</option>
              </select>
            </div>
          </div>
        </div>

        {/* Work */}
        <div className="form-section">
          <h3>💼 Work & Health</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Work Hours (per day)</label>
              <input type="number" name="Work_Hours" value={formData.Work_Hours} onChange={handleChange} min="0" max="16" required />
            </div>
            <div className="form-group">
              <label>Travel Time (hours/day)</label>
              <input type="number" name="Travel_Time" value={formData.Travel_Time} onChange={handleChange} min="0" max="6" step="0.5" required />
            </div>
            <div className="form-group">
              <label>Blood Pressure (systolic)</label>
              <input type="number" name="Blood_Pressure" value={formData.Blood_Pressure} onChange={handleChange} min="90" max="180" required />
            </div>
            <div className="form-group">
              <label>Cholesterol Level</label>
              <input type="number" name="Cholesterol_Level" value={formData.Cholesterol_Level} onChange={handleChange} min="100" max="300" required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Blood Sugar Level</label>
              <input type="number" name="Blood_Sugar_Level" value={formData.Blood_Sugar_Level} onChange={handleChange} min="60" max="200" required />
            </div>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '1rem' }} disabled={loading}>
          {loading ? 'Analyzing...' : '🔍 Analyze My Stress Level'}
        </button>
      </form>
    </div>
  );
}

export default StressForm;
