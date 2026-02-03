import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Recommendations() {
  const [stressLevel, setStressLevel] = useState('Medium');
  const [recommendations, setRecommendations] = useState([]);
  const [emergencyTips, setEmergencyTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isManageMode, setIsManageMode] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingRec, setEditingRec] = useState(null);
  const [formData, setFormData] = useState({ title: '', description: '', icon: '💡', stress_level: 'Medium' });
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

  const handleAddRecommendation = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/recommendations`, {
        ...formData,
        stress_level: stressLevel
      });
      setFormData({ title: '', description: '', icon: '💡', stress_level: stressLevel });
      setShowAddForm(false);
      handleLevelChange(stressLevel); // Refresh list
    } catch (err) {
      console.error('Error adding recommendation:', err);
      alert('Failed to add recommendation');
    }
  };

  const handleUpdateRecommendation = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API_URL}/recommendations/${editingRec.id}`, formData);
      setEditingRec(null);
      setFormData({ title: '', description: '', icon: '💡', stress_level: stressLevel });
      handleLevelChange(stressLevel); // Refresh list
    } catch (err) {
      console.error('Error updating recommendation:', err);
      alert('Failed to update recommendation');
    }
  };

  const handleDeleteRecommendation = async (recId) => {
    if (!window.confirm('Are you sure you want to delete this recommendation?')) return;
    try {
      await axios.delete(`${API_URL}/recommendations/${recId}`);
      handleLevelChange(stressLevel); // Refresh list
    } catch (err) {
      console.error('Error deleting recommendation:', err);
      alert('Failed to delete recommendation');
    }
  };

  const startEdit = (rec) => {
    setEditingRec(rec);
    setFormData({
      title: rec.title,
      description: rec.description,
      icon: rec.icon,
      stress_level: stressLevel
    });
    setShowAddForm(false);
  };

  const cancelEdit = () => {
    setEditingRec(null);
    setFormData({ title: '', description: '', icon: '💡', stress_level: stressLevel });
  };

  const commonEmojis = ['💡', '✅', '🧘', '🏃', '😴', '🌬️', '⏰', '☕', '👥', '🌳', '📝', '🛑', '💆', '🛏️', '📱', '💬', '🚶', '🚫', '🎵', '❤️', '🌟', '🎯', '🧠', '💪', '🌈'];

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

      {/* Management Toggle */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <button 
          className={`btn ${isManageMode ? 'btn-secondary' : 'btn-primary'}`}
          onClick={() => {
            setIsManageMode(!isManageMode);
            setShowAddForm(false);
            setEditingRec(null);
          }}
          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
        >
          {isManageMode ? '👁️ View Mode' : '⚙️ Manage Recommendations'}
        </button>
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

      {/* Add New Recommendation Button (Manage Mode) */}
      {isManageMode && !showAddForm && !editingRec && (
        <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(true)}
            style={{ padding: '0.75rem 2rem' }}
          >
            ➕ Add New Recommendation for {stressLevel} Stress
          </button>
        </div>
      )}

      {/* Add/Edit Form */}
      {(showAddForm || editingRec) && (
        <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%)', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
          <h3 style={{ marginBottom: '1.5rem', color: '#6366f1' }}>
            {editingRec ? '✏️ Edit Recommendation' : '➕ Add New Recommendation'}
          </h3>
          <form onSubmit={editingRec ? handleUpdateRecommendation : handleAddRecommendation}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Icon</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {commonEmojis.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => setFormData({ ...formData, icon: emoji })}
                    style={{
                      width: '40px',
                      height: '40px',
                      fontSize: '1.2rem',
                      border: formData.icon === emoji ? '2px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      background: formData.icon === emoji ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.05)',
                      cursor: 'pointer'
                    }}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter recommendation title"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'inherit',
                  fontSize: '1rem'
                }}
              />
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter recommendation description"
                required
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'inherit',
                  fontSize: '1rem',
                  resize: 'vertical'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
                {editingRec ? '💾 Save Changes' : '➕ Add Recommendation'}
              </button>
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => {
                  setShowAddForm(false);
                  cancelEdit();
                }}
                style={{ padding: '0.75rem 2rem' }}
              >
                ❌ Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Recommendations Grid */}
      <div className="recommendations-grid">
        {recommendations.map((rec, index) => (
          <div key={rec.id || index} className="recommendation-card" style={{ position: 'relative' }}>
            {isManageMode && (
              <div style={{ 
                position: 'absolute', 
                top: '0.5rem', 
                right: '0.5rem', 
                display: 'flex', 
                gap: '0.25rem' 
              }}>
                <button
                  onClick={() => startEdit(rec)}
                  style={{
                    background: 'rgba(99, 102, 241, 0.2)',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '0.25rem 0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDeleteRecommendation(rec.id)}
                  style={{
                    background: 'rgba(239, 68, 68, 0.2)',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '0.25rem 0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            )}
            <div className="recommendation-icon">{rec.icon}</div>
            <div className="recommendation-title">{rec.title}</div>
            <div className="recommendation-desc">{rec.description}</div>
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#888', fontSize: '1.1rem' }}>No recommendations found for {stressLevel} stress level.</p>
          {isManageMode && (
            <button 
              className="btn btn-primary" 
              onClick={() => setShowAddForm(true)}
              style={{ marginTop: '1rem' }}
            >
              ➕ Add First Recommendation
            </button>
          )}
        </div>
      )}

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
