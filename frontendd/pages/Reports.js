import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const API_URL = 'http://localhost:5000/api';

function Reports() {
  const user = JSON.parse(localStorage.getItem('user'));
  const [activeTab, setActiveTab] = useState('weekly');
  const [weeklyData, setWeeklyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [beforeAfter, setBeforeAfter] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchReports = async () => {
    try {
      const [weekly, monthly, ba] = await Promise.all([
        axios.get(`${API_URL}/reports/weekly/${user.user_id}`),
        axios.get(`${API_URL}/reports/monthly/${user.user_id}`),
        axios.get(`${API_URL}/reports/before-after/${user.user_id}`)
      ]);
      setWeeklyData(weekly.data);
      setMonthlyData(monthly.data);
      setBeforeAfter(ba.data);
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

  const getPieData = (data) => {
    if (!data?.distribution) return [];
    return [
      { name: 'Low', value: data.distribution.Low || 0 },
      { name: 'Medium', value: data.distribution.Medium || 0 },
      { name: 'High', value: data.distribution.High || 0 }
    ];
  };

  const renderReport = (data, period) => {
    if (!data || data.total_assessments === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <h3>No {period} Data Available</h3>
          <p>Complete stress assessments to see your {period.toLowerCase()} report</p>
        </div>
      );
    }

    const pieData = getPieData(data);

    return (
      <div className="report-content">
        {/* Stats Cards */}
        <div className="stats-grid" style={{ marginBottom: '2rem' }}>
          <div className="stat-card primary">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{data.total_assessments}</div>
            <div className="stat-label">Total Assessments</div>
          </div>
          <div className="stat-card" style={{ background: data.dominant_level === 'Low' ? 'var(--gradient-success)' : data.dominant_level === 'Medium' ? 'var(--gradient-warning)' : 'var(--gradient-danger)' }}>
            <div className="stat-icon">{data.dominant_level === 'Low' ? '😊' : data.dominant_level === 'Medium' ? '😐' : '😰'}</div>
            <div className="stat-value">{data.dominant_level}</div>
            <div className="stat-label">Dominant Level</div>
          </div>
        </div>

        {/* Distribution */}
        <div className="cards-grid">
          <div className="report-card">
            <h3>📈 Stress Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e1e2e', border: '1px solid #333' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="report-card">
            <h3>📊 Level Breakdown</h3>
            <div style={{ marginTop: '1.5rem' }}>
              {['Low', 'Medium', 'High'].map((level, index) => (
                <div key={level} style={{ marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span>{level === 'Low' ? '😊' : level === 'Medium' ? '😐' : '😰'} {level}</span>
                    <span>{data.percentages?.[level] || 0}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className={`progress-fill ${level.toLowerCase()}`}
                      style={{ width: `${data.percentages?.[level] || 0}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="reports-container">
      <div className="dashboard-header">
        <h1>📈 Stress Reports</h1>
        <p>Analyze your stress patterns over time</p>
      </div>

      {/* Tab Navigation */}
      <div className="report-tabs">
        <button
          className={`report-tab ${activeTab === 'weekly' ? 'active' : ''}`}
          onClick={() => setActiveTab('weekly')}
        >
          📅 Weekly Report
        </button>
        <button
          className={`report-tab ${activeTab === 'monthly' ? 'active' : ''}`}
          onClick={() => setActiveTab('monthly')}
        >
          📆 Monthly Report
        </button>
        <button
          className={`report-tab ${activeTab === 'progress' ? 'active' : ''}`}
          onClick={() => setActiveTab('progress')}
        >
          📊 Before/After
        </button>
      </div>

      {/* Report Content */}
      {activeTab === 'weekly' && renderReport(weeklyData, 'Weekly')}
      {activeTab === 'monthly' && renderReport(monthlyData, 'Monthly')}
      
      {activeTab === 'progress' && (
        <div>
          {beforeAfter?.before ? (
            <div className="report-card">
              <h3 style={{ marginBottom: '2rem', textAlign: 'center' }}>📊 Your Progress Journey</h3>
              
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-around',
                padding: '2rem',
                background: 'rgba(255,255,255,0.02)',
                borderRadius: '16px'
              }}>
                {/* Before */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '1rem' }}>🏁 First Assessment</div>
                  <div style={{ 
                    fontSize: '4rem',
                    marginBottom: '0.5rem'
                  }}>
                    {beforeAfter.before.level === 'Low' ? '😊' : beforeAfter.before.level === 'Medium' ? '😐' : '😰'}
                  </div>
                  <div className={`stress-badge ${beforeAfter.before.level.toLowerCase()}`} style={{ fontSize: '1.1rem', padding: '0.75rem 1.5rem' }}>
                    {beforeAfter.before.level}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '1rem' }}>
                    {new Date(beforeAfter.before.date).toLocaleDateString()}
                  </div>
                </div>

                {/* Arrow */}
                <div style={{ 
                  fontSize: '3rem',
                  color: beforeAfter.improvement === 'Improved' ? '#10b981' : beforeAfter.improvement === 'Declined' ? '#ef4444' : '#f59e0b',
                  animation: 'pulse 2s infinite'
                }}>
                  {beforeAfter.improvement === 'Improved' ? '→ 🎉' : beforeAfter.improvement === 'Declined' ? '→ ⚠️' : '→'}
                </div>

                {/* After */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '1rem' }}>🎯 Latest Assessment</div>
                  <div style={{ 
                    fontSize: '4rem',
                    marginBottom: '0.5rem'
                  }}>
                    {beforeAfter.after.level === 'Low' ? '😊' : beforeAfter.after.level === 'Medium' ? '😐' : '😰'}
                  </div>
                  <div className={`stress-badge ${beforeAfter.after.level.toLowerCase()}`} style={{ fontSize: '1.1rem', padding: '0.75rem 1.5rem' }}>
                    {beforeAfter.after.level}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '1rem' }}>
                    {new Date(beforeAfter.after.date).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {/* Message */}
              <div style={{ 
                textAlign: 'center', 
                marginTop: '2rem',
                padding: '1.5rem',
                background: beforeAfter.improvement === 'Improved' ? 'rgba(16, 185, 129, 0.1)' : beforeAfter.improvement === 'Declined' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                borderRadius: '12px',
                color: beforeAfter.improvement === 'Improved' ? '#10b981' : beforeAfter.improvement === 'Declined' ? '#ef4444' : '#f59e0b',
                fontSize: '1.1rem',
                fontWeight: '500'
              }}>
                {beforeAfter.message}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>Not Enough Data</h3>
              <p>Complete at least 2 stress assessments to see your progress</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Reports;
