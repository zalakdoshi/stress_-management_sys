import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const API_URL = 'http://localhost:5000/api';

function Dashboard() {
  const user = JSON.parse(localStorage.getItem('user'));
  const [history, setHistory] = useState([]);
  const [report, setReport] = useState(null);
  const [beforeAfter, setBeforeAfter] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = async () => {
    try {
      const [historyRes, weeklyRes, beforeAfterRes] = await Promise.all([
        axios.get(`${API_URL}/history/${user.user_id}`),
        axios.get(`${API_URL}/reports/weekly/${user.user_id}`),
        axios.get(`${API_URL}/reports/before-after/${user.user_id}`)
      ]);
      setHistory(historyRes.data.history || []);
      setReport(weeklyRes.data);
      setBeforeAfter(beforeAfterRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStressColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#6366f1';
    }
  };

  const chartData = history.slice(0, 10).reverse().map((item, index) => ({
    name: `Day ${index + 1}`,
    value: item.stress_level === 'Low' ? 1 : item.stress_level === 'Medium' ? 2 : 3,
    level: item.stress_level
  }));

  const pieData = report?.distribution ? [
    { name: 'Low', value: report.distribution.Low || 0, color: '#10b981' },
    { name: 'Medium', value: report.distribution.Medium || 0, color: '#f59e0b' },
    { name: 'High', value: report.distribution.High || 0, color: '#ef4444' }
  ] : [];

  const latestStress = history[0]?.stress_level || 'Unknown';

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name}! 👋</h1>
        <p>Here's your stress management overview</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className={`stat-card ${latestStress.toLowerCase()}`} style={{ background: `linear-gradient(135deg, ${getStressColor(latestStress)} 0%, ${getStressColor(latestStress)}99 100%)` }}>
          <div className="stat-header">
            <span className="stat-icon">🎯</span>
          </div>
          <div className="stat-value">{latestStress}</div>
          <div className="stat-label">Current Stress Level</div>
        </div>

        <div className="stat-card primary">
          <div className="stat-header">
            <span className="stat-icon">📊</span>
          </div>
          <div className="stat-value">{history.length}</div>
          <div className="stat-label">Total Assessments</div>
        </div>

        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)' }}>
          <div className="stat-header">
            <span className="stat-icon">📈</span>
          </div>
          <div className="stat-value">{beforeAfter?.improvement || 'N/A'}</div>
          <div className="stat-label">Progress Status</div>
        </div>

        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)' }}>
          <div className="stat-header">
            <span className="stat-icon">🎯</span>
          </div>
          <div className="stat-value">{report?.dominant_level || 'N/A'}</div>
          <div className="stat-label">Weekly Dominant</div>
        </div>
      </div>

      {/* Charts */}
      <div className="cards-grid">
        <div className="chart-container">
          <div className="chart-header">
            <h3>📈 Stress Trend (Last 10 Assessments)</h3>
          </div>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" stroke="#888" />
                <YAxis domain={[0, 4]} ticks={[1, 2, 3]} tickFormatter={(v) => ['', 'Low', 'Med', 'High'][v]} stroke="#888" />
                <Tooltip 
                  contentStyle={{ background: '#1e1e2e', border: '1px solid #333' }}
                  formatter={(value, name) => [['', 'Low', 'Medium', 'High'][value], 'Stress']}
                />
                <Line type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>No Data Yet</h3>
              <p>Complete your first stress assessment to see trends</p>
            </div>
          )}
        </div>

        <div className="chart-container">
          <div className="chart-header">
            <h3>🥧 Weekly Distribution</h3>
          </div>
          {pieData.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e1e2e', border: '1px solid #333' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">🥧</div>
              <h3>No Weekly Data</h3>
              <p>Start tracking your stress levels</p>
            </div>
          )}
        </div>
      </div>

      {/* Before/After Comparison */}
      {beforeAfter?.before && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>📊 Before & After Analysis</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', padding: '1rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>First Assessment</div>
              <div className={`stress-badge ${beforeAfter.before.level.toLowerCase()}`}>
                {beforeAfter.before.level}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
                {new Date(beforeAfter.before.date).toLocaleDateString()}
              </div>
            </div>
            <div style={{ fontSize: '2rem' }}>→</div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Latest Assessment</div>
              <div className={`stress-badge ${beforeAfter.after.level.toLowerCase()}`}>
                {beforeAfter.after.level}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
                {new Date(beforeAfter.after.date).toLocaleDateString()}
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: beforeAfter.improvement === 'Improved' ? '#10b981' : beforeAfter.improvement === 'Declined' ? '#ef4444' : '#f59e0b' }}>
            {beforeAfter.message}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="cards-grid" style={{ marginTop: '1.5rem' }}>
        <Link to="/assess" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.3s', ':hover': { transform: 'translateY(-4px)' } }}>
            <div className="card-header">
              <div className="card-icon primary">🧠</div>
              <div>
                <h3>Take Stress Assessment</h3>
                <p style={{ color: '#888', fontSize: '0.9rem' }}>Check your current stress level</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/recommendations" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer' }}>
            <div className="card-header">
              <div className="card-icon success">💡</div>
              <div>
                <h3>Get Recommendations</h3>
                <p style={{ color: '#888', fontSize: '0.9rem' }}>Personalized stress relief tips</p>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/chatbot" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer' }}>
            <div className="card-header">
              <div className="card-icon warning">🤖</div>
              <div>
                <h3>Talk to AI Support</h3>
                <p style={{ color: '#888', fontSize: '0.9rem' }}>Get instant stress relief help</p>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;
