import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = ({ onLogout }) => {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const dataCap = 20; // 20GB monthly cap

  const filteredStudents = students.filter((student) =>
    student.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    // Load sample student data
    const sampleData = [
      { id: "STU001", usage: 15.5 },
      { id: "STU002", usage: 22.8 },
      { id: "STU003", usage: 8.2 },
      { id: "STU004", usage: 19.1 },
      { id: "STU005", usage: 25.3 }
    ];
    setStudents(sampleData);
  }, []);

  const exceededStudents = students.filter((s) => s.usage >= dataCap);

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      onLogout();
    }
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>WiFi Admin Dashboard</h1>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <div className="dashboard-controls">
        <input
          type="text"
          placeholder="Search by student ID"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-bar"
        />
      </div>

      {exceededStudents.length > 0 && (
        <div className="alert">
          {exceededStudents.length} student{exceededStudents.length > 1 ? 's have' : ' has'} exceeded the data cap!
        </div>
      )}

      <table className="students-table">
        <thead>
          <tr>
            <th>Student ID</th>
            <th>Usage (GB)</th>
            <th>Cap (%)</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {filteredStudents.map((student) => {
            const percent = Math.round((student.usage / dataCap) * 100);
            const status =
              percent >= 100
                ? 'Exceeded'
                : percent >= 80
                ? 'Warning'
                : 'OK';

            return (
              <tr key={student.id} className={status === 'Exceeded' ? 'exceeded-row' : ''}>
                <td>{student.id}</td>
                <td>{student.usage}</td>
                <td>{percent}%</td>
                <td>
                  <span className={status.toLowerCase()}>{status}</span>
                </td>
                <td>
                  <button
                    className="reset-button"
                    onClick={() => {
                      const resetData = students.map((s) =>
                        s.id === student.id ? { ...s, usage: 0 } : s
                      );
                      setStudents(resetData);
                    }}
                  >
                    Reset Cap
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default AdminDashboard;