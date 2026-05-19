import studentsData from '../students.json';
import React, { useEffect, useState } from 'react';
import '../styles/Reports.css';
import { saveAs } from 'file-saver';

function Reports() {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setStudents(studentsData);
  }, []);

  const filtered = students.filter((s) =>
    s.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const downloadCSV = () => {
    const csvHeader = "Student ID, Usage (GB)\n";
    const csvRows = filtered.map((s) => `${s.id}, ${s.usage}`).join('\n');
    const blob = new Blob([csvHeader + csvRows], { type: 'text/csv;charset=utf-8' });
    saveAs(blob, 'student_usage_report.csv');
  };

  return (
    <>
        <div className="reports-container">
          <h2>Usage Reports</h2>
          <input
            type="text"
            placeholder="Search by student ID"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="report-search"
          />

          <table>
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Usage (GB)</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((student) => (
                <tr key={student.id}>
                  <td>{student.id}</td>
                  <td>{student.usage}</td>
                </tr>
              ))}
            </tbody>
          </table>

        <button onClick={downloadCSV} className="download-button">Download CSV</button>
      </div>
    </>
  );
}

export default Reports;
