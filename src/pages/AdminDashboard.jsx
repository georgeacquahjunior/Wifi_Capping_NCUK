import React, { useState, useEffect } from "react";
import "../styles/AdminDashboard.css";
import { apiFetch } from "../utils/api"; // 🔥 Reusable API helper

export default function AdminDashboard() {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  //  Fetch Students from Backend
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        setError("");

        const res = await apiFetch(
          "https://wifi-capping-ncuk-1.onrender.com/usage_logs/dashboard"
        );

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.error || "Failed to fetch students");
        }

        const data = await res.json();
        setStudents(data.students || []);
      } catch (err) {
        console.error("Error fetching students:", err);
        setError("Failed to load student data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  //  Filter students by ID
  const filteredStudents = students.filter((student) =>
    student.student_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="dashboard-container">
      <h1>WiFi Admin Dashboard</h1>

      {/*  Search Bar */}
      <input
        type="text"
        placeholder="Search by Student ID"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-bar"
      />

      {/*  Loading State */}
      {loading && <p className="loading">Loading students...</p>}

      {/* Error State */}
      {error && <p className="error">{error}</p>}

      {/* Students Table */}
      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>STUDENT ID</th>
              <th>FIRST NAME</th>
              <th>LAST NAME</th>
              <th>DATE ALLOCATED</th>
              <th>DATA ALLOCATED (GB)</th>
              <th>DATA USED (GB)</th>
              <th>DATA LEFT (GB)</th>
              <th>% USED</th>
              <th>STATUS</th>
            </tr>
          </thead>

          <tbody>
            {filteredStudents.length > 0 ? (
              filteredStudents.map((student) => (
                <tr key={student.student_id}>
                  <td data-label="Student ID">{student.student_id}</td>
                  <td data-label="First Name">{student.first_name}</td>
                  <td data-label="Last Name">{student.last_name}</td>
                  <td data-label="Date Allocated">{student.date_allocated || "—"}</td>
                  <td data-label="Data Allocated (GB)">{student.data_allocated}</td>
                  <td data-label="Data Used (GB)">{student.data_used}</td>
                  <td data-label="Data Left (GB)">{student.data_left}</td>
                  <td data-label="% Used">{student.percentage_used}%</td>
                  <td data-label="Status">
                    <span className={`status ${student.capped_status?.toLowerCase()}`}>
                      {student.capped_status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9" style={{ textAlign: "center" }}>
                  No students found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
