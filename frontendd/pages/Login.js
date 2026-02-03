import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/login`, formData);
      localStorage.setItem('user', JSON.stringify(response.data));
      navigate('/dashboard');
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      {/* Animated Background Shapes */}
      <div className="auth-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
        <div className="shape shape-4"></div>
        <div className="shape shape-5"></div>
      </div>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo-wrapper">
            <div className="auth-logo">🧘</div>
            <div className="auth-logo-ring"></div>
          </div>
          <h1>Welcome Back!</h1>
          <p>Sign in to continue your wellness journey</p>
        </div>

        {error && (
          <div className="auth-error">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className={`floating-input ${focusedField === 'email' || formData.email ? 'focused' : ''}`}>
            <input
              type="email"
              name="email"
              id="email"
              value={formData.email}
              onChange={handleChange}
              onFocus={() => setFocusedField('email')}
              onBlur={() => setFocusedField('')}
              required
            />
            <label htmlFor="email">
              <span className="label-icon">📧</span>
              Email Address
            </label>
            <div className="input-highlight"></div>
          </div>

          <div className={`floating-input ${focusedField === 'password' || formData.password ? 'focused' : ''}`}>
            <input
              type="password"
              name="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
              onFocus={() => setFocusedField('password')}
              onBlur={() => setFocusedField('')}
              required
            />
            <label htmlFor="password">
              <span className="label-icon">🔒</span>
              Password
            </label>
            <div className="input-highlight"></div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? (
              <div className="btn-loader">
                <span></span>
                <span></span>
                <span></span>
              </div>
            ) : (
              <>
                <span>Sign In</span>
                <span className="btn-icon">→</span>
              </>
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <div className="auth-footer">
          <p>Don't have an account?</p>
          <Link to="/register" className="auth-link">
            Create Account
            <span className="link-arrow">→</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
