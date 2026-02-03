import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
    window.location.reload();
  };

  const menuItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/assess', icon: '🧠', label: 'Stress Check' },
    { path: '/recommendations', icon: '💡', label: 'Recommendations' },
    { path: '/journal', icon: '📝', label: 'Mood Journal' },
    { path: '/reports', icon: '📈', label: 'Reports' },
    { path: '/chatbot', icon: '🤖', label: 'AI Support' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <span className="logo-icon">🧘</span>
        <span>StressLess</span>
      </div>

      <div className="navbar-menu">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </div>

      <div className="nav-user">
        <div className="nav-user-info">
          <div className="nav-user-avatar">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <span className="nav-user-name">{user?.name || 'User'}</span>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
