import React, { useState } from 'react';
import '../styles/Settings.css';

const Settings = () => {
  const [dataCap, setDataCap] = useState(20);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleDataCapChange = (e) => {
    setDataCap(e.target.value);
  };

  const handleResetAllUsage = () => {
    alert("All student data usage has been reset (placeholder logic).");
  };

  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      alert("Passwords do not match.");
    } else {
      alert("Password changed (placeholder logic).");
    }
  };

  return (
    <>
      <div className="settings-container">
        <h2>System Settings</h2>

        <div className="section">
          <label>Monthly Data Cap (GB):</label>
          <input
            type="number"
            value={dataCap}
            onChange={handleDataCapChange}
            min="1"
          />
        </div>

        <div className="section">
          <h3>Change Admin Password</h3>
          <form onSubmit={handlePasswordChange}>
            <input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <button className="update-password-button" type="submit">Update Password</button>
          </form>
        </div>

        <div className="section">
          <button className="reset-all-button" onClick={handleResetAllUsage}>
            Reset All Student Usage
          </button>
        </div>
      </div>
    </>
  );
};

export default Settings;
