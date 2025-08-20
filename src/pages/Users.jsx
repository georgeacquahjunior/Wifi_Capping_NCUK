import React, { useState, useEffect } from "react";
import studentsData from '../students.json';
import "../styles/Users.css";
import ResetButton from '../components/ResetButton';
import { useNavigate } from 'react-router-dom';

function Users() {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);
  const [formData, setFormData] = useState({ id: "", usage: "" });

 useEffect(() => {
     setStudents(studentsData);
   }, []);

  const handleSearchChange = (e) => setSearchTerm(e.target.value);

  const handleFormChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleAdd = () => {
    if (!formData.id || formData.usage === "") return alert("Fill all fields");
    setStudents([...students, { ...formData, usage: parseFloat(formData.usage) }]);
    setFormData({ id: "", usage: "" });
  };

  const handleEdit = (index) => {
    setEditingIndex(index);
    setFormData(students[index]);
  };

  const handleUpdate = () => {
    const updated = [...students];
    updated[editingIndex] = { ...formData, usage: parseFloat(formData.usage) };
    setStudents(updated);
    setEditingIndex(null);
    setFormData({ id: "", usage: "" });
  };

  const handleDelete = (index) => {
    if (window.confirm("Delete this student?")) {
      const filtered = students.filter((_, i) => i !== index);
      setStudents(filtered);
    }
  };

  const filteredStudents = students.filter((student) =>
    student.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const navigate = useNavigate();

  return (
    <>
      <div className="users-container">
        <h2>Manage Students</h2>

        <input
          type="text"
          placeholder="Search by ID"
          value={searchTerm}
          onChange={handleSearchChange}
          className="search-input"
        />

        <div className="form-container">
          <input
            type="text"
            name="id"
            placeholder="Student ID"
            value={formData.id}
            onChange={handleFormChange}
          />
          <input
            type="number"
            name="usage"
            placeholder="Usage (GB)"
            value={formData.usage}
            onChange={handleFormChange}
          />
          {editingIndex === null ? (
            <button className="add-button" onClick={handleAdd}>Add</button>
          ) : (
            <button className="update-button" onClick={handleUpdate}>Update</button>
          )}
        </div>

        <table>
          <thead>
            <tr>
              <th>Student ID</th>
              <th>Usage (GB)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((student, index) => (
              <tr key={index}>
                <td>{student.id}</td>
                <td>{student.usage}</td>
                <td>
                  <button className="edit-button" onClick={() => handleEdit(index)}>Edit</button>
                  <button className="delete-button" onClick={() => handleDelete(index)}>Delete</button>
                    <ResetButton
                        studentId={student.id}
                        students={students}
                        setStudents={setStudents}
                      />
                </td>
              </tr>
            ))}
            {filteredStudents.length === 0 && (
              <tr>
                <td colSpan="3">No matching students.</td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="admin-actions">
            <button onClick={() => navigate('/add-admin')}>
              Add Admin
            </button>

            <button onClick={() => navigate('/add-student')}>
              Add Student
            </button>
        </div>
        
      </div>
    </>

  );
}

export default Users;


