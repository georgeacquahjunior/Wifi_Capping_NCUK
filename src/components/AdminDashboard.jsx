import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = () => {
  // 1️: Sample student data in state
  const [students, setStudents] = useState([
    /*{ id: 'STU001', usage: 15.6 },
    { id: 'STU002', usage: 20.4 },
    { id: 'STU003', usage: 8.2 },*/
   ]);

  const dataCap = 20; // 20GB monthly cap

    useEffect(() => {
    fetch('/students.json')
      .then((res) => res.json())
      .then((data) => setStudents(data))
      .catch((err) => console.error("Error loading students:", err));
    }, []);

  // 2️: Render table rows dynamically
  return (
    <div className="dashboard-container">
      <h1>WiFi Admin Dashboard</h1>

      <table>
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
          {students.map((student) => {
            const percent = Math.round((student.usage / dataCap) * 100);
            const status =
              percent >= 100
                ? 'Exceeded'
                : percent >= 80
                ? 'Warning'
                : 'OK';

            return (
              <tr key={student.id}>
                <td>{student.id}</td>
                <td>{student.usage}</td>
                <td>{percent}%</td>
                <td>
                  <span className={status.toLowerCase()}>{status}</span>
                </td>
                <td>
                  <button
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

/*import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [students, setStudents] = useState([]);
  const dataCap = 20;

  useEffect(() => {
    fetch('/students.json')
      .then((res) => res.json())
      .then((data) => setStudents(data))
      .catch((err) => console.error("Error loading students:", err));
  }, []);
*/