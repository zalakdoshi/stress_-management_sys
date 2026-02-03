import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Recommendations() {
  const [stressLevel, setStressLevel] = useState('Medium');
  const [recommendations, setRecommendations] = useState([]);
  const [emergencyTips, setEmergencyTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = async () => {
    try {
      // Get latest stress level from history
      const historyRes = await axios.get(`${API_URL}/history/${user.user_id}`);
      const latestLevel = historyRes.data.history?.[0]?.stress_level || 'Medium';
      setStressLevel(latestLevel);

      // Get recommendations for that level
      const recsRes = await axios.get(`${API_URL}/recommendations/${latestLevel}`);
      setRecommendations(recsRes.data.recommendations || []);

      // Get emergency tips
      const emergencyRes = await axios.get(`${API_URL}/emergency-tips`);
      setEmergencyTips(emergencyRes.data.tips || []);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLevelChange = async (level) => {
    setStressLevel(level);
    try {
      const recsRes = await axios.get(`${API_URL}/recommendations/${level}`);
      setRecommendations(recsRes.data.recommendations || []);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="dashboard-header">
        <h1>💡 Personalized Recommendations</h1>
        <p>Based on your stress level: <span className={`stress-badge ${stressLevel.toLowerCase()}`}>{stressLevel}</span></p>
      </div>

      {/* Stress Level Selector */}
      <div className="report-tabs" style={{ marginBottom: '2rem' }}>
        {['Low', 'Medium', 'High'].map((level) => (
          <button
            key={level}
            className={`report-tab ${stressLevel === level ? 'active' : ''}`}
            onClick={() => handleLevelChange(level)}
          >
            {level === 'Low' ? '😊' : level === 'Medium' ? '😐' : '😰'} {level} Stress
          </button>
        ))}
      </div>

      {/* Recommendations Grid */}
      <div className="recommendations-grid">
        {recommendations.map((rec, index) => (
          <div key={index} className="recommendation-card">
            <div className="recommendation-icon">{rec.icon}</div>
            <div className="recommendation-title">{rec.title}</div>
            <div className="recommendation-desc">{rec.description}</div>
          </div>
        ))}
      </div>

      {/* Emergency Section */}
      <div className="card" style={{ marginTop: '2rem', background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
        <h3 style={{ marginBottom: '1.5rem', color: '#ef4444' }}>🚨 Emergency Stress Relief (S.T.O.P. Technique)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {emergencyTips.map((tip, index) => (
            <div key={index} style={{ 
              background: 'rgba(255, 255, 255, 0.05)', 
              padding: '1rem', 
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '50%', 
                background: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 0.75rem',
                fontWeight: '700'
              }}>
                {tip.step}
              </div>
              <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{tip.title}</div>
              <div style={{ color: '#888', fontSize: '0.85rem' }}>{tip.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Additional Tips */}
      <div className="cards-grid" style={{ marginTop: '2rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>🎵 Relaxing Activities</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>🎧 Listen to calming music</li>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>📚 Read a book</li>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>🛁 Take a warm bath</li>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>🌿 Spend time in nature</li>
            <li style={{ padding: '0.5rem 0' }}>🎨 Try creative activities</li>
          </ul>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>🧘 Breathing Exercises</h3>
          <div style={{ marginBottom: '1rem' }}>
            <strong>4-7-8 Technique:</strong>
            <p style={{ color: '#888', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Inhale for 4 seconds → Hold for 7 seconds → Exhale for 8 seconds
            </p>
          </div>
          <div>
            <strong>Box Breathing:</strong>
            <p style={{ color: '#888', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Inhale 4s → Hold 4s → Exhale 4s → Hold 4s → Repeat
            </p>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>📱 Helpful Resources</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>🧘 Headspace - Meditation App</li>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>🌙 Calm - Sleep & Relaxation</li>
            <li style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>💪 Nike Training - Exercise</li>
            <li style={{ padding: '0.5rem 0' }}>📝 Daylio - Mood Journal</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Recommendations;
