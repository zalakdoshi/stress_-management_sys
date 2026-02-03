import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import StressForm from './pages/StressForm';
import Recommendations from './pages/Recommendations';
import Journal from './pages/Journal';
import Reports from './pages/Reports';
import Chatbot from './pages/Chatbot';
import './App.css';

function App() {
  const user = JSON.parse(localStorage.getItem('user'));

  return (
    <Router>
      <div className="app">
        {user && <Navbar />}
        <div className="main-content">
          <Routes>
            <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/assess" element={user ? <StressForm /> : <Navigate to="/login" />} />
            <Route path="/recommendations" element={user ? <Recommendations /> : <Navigate to="/login" />} />
            <Route path="/journal" element={user ? <Journal /> : <Navigate to="/login" />} />
            <Route path="/reports" element={user ? <Reports /> : <Navigate to="/login" />} />
            <Route path="/chatbot" element={user ? <Chatbot /> : <Navigate to="/login" />} />
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
