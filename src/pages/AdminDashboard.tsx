import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import './AdminDashboard.css';

const AdminDashboard: React.FC = () => {
  const { state, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>WiFi Capping NCUK - Admin Dashboard</h1>
          <div className="user-info">
            <span>Welcome, {state.user?.username}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>System Status</h3>
            <div className="status-indicator active">
              <span className="status-dot"></span>
              WiFi Capping System Active
            </div>
            <p>Last updated: {new Date().toLocaleString()}</p>
          </div>

          <div className="dashboard-card">
            <h3>Connected Users</h3>
            <div className="metric">
              <span className="metric-number">24</span>
              <span className="metric-label">Active Connections</span>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Data Usage Today</h3>
            <div className="metric">
              <span className="metric-number">1.2 GB</span>
              <span className="metric-label">Total Usage</span>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Bandwidth Limit</h3>
            <div className="metric">
              <span className="metric-number">10 Mbps</span>
              <span className="metric-label">Current Limit</span>
            </div>
          </div>

          <div className="dashboard-card wide">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              <button className="action-button">Manage Users</button>
              <button className="action-button">View Reports</button>
              <button className="action-button">System Settings</button>
              <button className="action-button">Network Configuration</button>
            </div>
          </div>

          <div className="dashboard-card wide">
            <h3>Recent Activity</h3>
            <div className="activity-list">
              <div className="activity-item">
                <span className="activity-time">10:30 AM</span>
                <span className="activity-desc">User john_doe connected</span>
              </div>
              <div className="activity-item">
                <span className="activity-time">10:15 AM</span>
                <span className="activity-desc">Bandwidth limit adjusted to 10 Mbps</span>
              </div>
              <div className="activity-item">
                <span className="activity-time">09:45 AM</span>
                <span className="activity-desc">System backup completed</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;