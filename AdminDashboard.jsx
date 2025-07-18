import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = () => {
  // 1️: Sample student data in state
  const [students, setStudents] = useState([]);

   const [searchTerm, setSearchTerm] = useState('');
 
    const dataCap = 20; // 20GB monthly cap

    const filteredStudents = students.filter((student) =>
      student.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    useEffect(() => {
    fetch('/students.json')
      .then((res) => res.json())
      .then((data) => setStudents(data))
      .catch((err) => console.error("Error loading students:", err));
    }, []);

    const exceededStudents = students.filter((s) => {
      return s.usage >= dataCap;
    });

  // 2️: Render table rows dynamically
  return (
    <div className="dashboard-container">
      <h1>WiFi Admin Dashboard</h1>

      <input type= 'text' placeholder= 'search by student ID'
        value={searchTerm} onChange= {(e) =>setSearchTerm(e.target.value)} className= 'search-bar' /> 

          {exceededStudents.length > 0 && (
            <div className="alert">
              {exceededStudents.length} student{exceededStudents.length > 1 ? 's have' : ' has'} exceeded the data cap!
            </div>)
          }

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

/*{exceededStudents.length > 0 && (
  <div className="alert">
    🚨 {exceededStudents.length} student{exceededStudents.length > 1 ? 's have' : ' has'} exceeded the data cap!
  </div>
)}

.alert {
  background-color: #dc3545;
  color: white;
  padding: 15px;
  border-radius: 10px;
  font-weight: bold;
  margin-bottom: 20px;
}
  */