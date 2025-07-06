import React from 'react';
import './AdminDashboard.css';

const AdminDashboard = () => {
  return (
    <div className="dashboard-container">
      <h1>WiFi Admin Dashboard</h1>

      <table>
        <thead>
          <tr>
            <th>Student ID</th>
            <th>Data Used (GB)</th>
            <th>Cap (%)</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>STU001</td>
            <td>15.6</td>
            <td>78%</td>
            <td><span className="ok">OK</span></td>
            <td><button>Reset</button></td>
          </tr>
          <tr>
            <td>STU002</td>
            <td>20.4</td>
            <td>102%</td>
            <td><span className="over">Exceeded</span></td>
            <td><button>Reset</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default AdminDashboard;