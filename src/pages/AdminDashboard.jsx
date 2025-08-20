import studentsData from '../students.json'; // adjust path as needed
import React, { useState, useEffect } from 'react';
import '../styles/AdminDashboard.css';
import ResetButton from '../components/ResetButton';

export default function AdminDashboard() {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const dataCap = 20;

  // Load students data on mount
  useEffect(() => {
    setStudents(studentsData);
  }, []);

  const filteredStudents = students.filter((student) =>
    student.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const exceededStudents = students.filter((s) => s.usage >= dataCap);

  return (
    <>
      <div className="dashboard-container">
        <h1>WiFi Admin Dashboard</h1>

        <input
          type="text"
          placeholder="search by student ID"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-bar"
        />

        {exceededStudents.length > 0 && (
          <div className="alert">
            {exceededStudents.length} student
            {exceededStudents.length > 1 ? 's have' : ' has'} exceeded the data
            cap!
          </div>
        )}

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
                <tr
                  key={student.id}
                  className={status === 'Exceeded' ? 'exceeded-row' : ''}
                >
                  <td>{student.id}</td>
                  <td>{student.usage}</td>
                  <td>{percent}%</td>
                  <td>
                    <span className={status.toLowerCase()}>{status}</span>
                  </td>
                  <td>
                    <ResetButton
                      studentId={student.id}
                      setStudents={setStudents}
                      students={students}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
