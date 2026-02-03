import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Journal() {
  const user = JSON.parse(localStorage.getItem('user'));
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ mood: '😊', notes: '' });
  const [submitting, setSubmitting] = useState(false);

  const moods = [
    { emoji: '😊', label: 'Happy' },
    { emoji: '😌', label: 'Calm' },
    { emoji: '😐', label: 'Neutral' },
    { emoji: '😔', label: 'Sad' },
    { emoji: '😰', label: 'Anxious' },
    { emoji: '😤', label: 'Stressed' },
    { emoji: '😴', label: 'Tired' },
    { emoji: '🤗', label: 'Grateful' }
  ];

  useEffect(() => {
    fetchEntries();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchEntries = async () => {
    try {
      const response = await axios.get(`${API_URL}/journal/${user.user_id}`);
      setEntries(response.data.entries || []);
    } catch (err) {
      console.error('Error fetching journal:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await axios.post(`${API_URL}/journal`, {
        user_id: user.user_id,
        mood: formData.mood,
        notes: formData.notes
      });
      setFormData({ mood: '😊', notes: '' });
      setShowForm(false);
      fetchEntries();
    } catch (err) {
      console.error('Error adding entry:', err);
      alert('Failed to add entry. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="journal-container">
      <div className="dashboard-header">
        <h1>📝 Mood Journal</h1>
        <p>Track your daily mood and thoughts to identify patterns</p>
      </div>

      {/* Add Entry Button */}
      <button 
        className="btn btn-primary" 
        style={{ marginBottom: '2rem' }}
        onClick={() => setShowForm(!showForm)}
      >
        {showForm ? '✕ Close' : '+ Add New Entry'}
      </button>

      {/* Entry Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>How are you feeling today?</h3>
          <form onSubmit={handleSubmit}>
            {/* Mood Selector */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.75rem', color: '#888' }}>Select your mood</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                {moods.map((mood) => (
                  <button
                    key={mood.emoji}
                    type="button"
                    onClick={() => setFormData({ ...formData, mood: mood.emoji })}
                    style={{
                      padding: '0.75rem 1rem',
                      background: formData.mood === mood.emoji ? 'var(--gradient-primary)' : 'rgba(255,255,255,0.05)',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '0.25rem',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <span style={{ fontSize: '1.5rem' }}>{mood.emoji}</span>
                    <span style={{ fontSize: '0.75rem', color: formData.mood === mood.emoji ? 'white' : '#888' }}>{mood.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Notes */}
            <div className="form-group">
              <label>Notes (optional)</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows="4"
                placeholder="Write about your day, thoughts, or anything on your mind..."
                style={{ resize: 'vertical' }}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Saving...' : '💾 Save Entry'}
            </button>
          </form>
        </div>
      )}

      {/* Entries List */}
      {entries.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <h3>No journal entries yet</h3>
          <p>Start tracking your mood to identify patterns</p>
        </div>
      ) : (
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Recent Entries ({entries.length})</h3>
          {entries.map((entry) => (
            <div key={entry.id} className="journal-entry">
              <div className="journal-entry-header">
                <span className="journal-mood">{entry.mood}</span>
                <span className="journal-date">{formatDate(entry.entry_date)}</span>
              </div>
              {entry.notes && (
                <p className="journal-notes">{entry.notes}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Mood Summary */}
      {entries.length > 0 && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>📊 Mood Summary (Last 30 Days)</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            {moods.map((mood) => {
              const count = entries.filter(e => e.mood === mood.emoji).length;
              return (
                <div key={mood.emoji} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem',
                  background: 'rgba(255,255,255,0.05)',
                  padding: '0.5rem 1rem',
                  borderRadius: '50px'
                }}>
                  <span>{mood.emoji}</span>
                  <span style={{ color: '#888' }}>{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default Journal;
