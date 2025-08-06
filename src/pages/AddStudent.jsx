import React, { useState } from "react";
import '../styles/AddStudent.css'; 
import Navbar from "../components/Navbar";

const AddStudent = () => {
  const [formData, setFormData] = useState({
    studentId: "",
    firstName: "",
    lastName: "",
    password: "",
  });

  const [message, setMessage] = useState("");

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // TODO: Replace this with a real API call (e.g., fetch or axios)
    console.log("New student submitted:", formData);

    setMessage("✅ Student added successfully!");
    setFormData({
      studentId: "",
      firstName: "",
      lastName: "",
      password: "",
    });
  };

  return (
    <>
      <Navbar />
      <div className="add-student-container">
        <h2>Add New Student</h2>

        <form onSubmit={handleSubmit} className="add-student-form">
          <input
            type="text"
            name="studentId"
            placeholder="Student ID"
            value={formData.studentId}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={formData.firstName}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <button type="submit">Add Student</button>
        </form>

        {message && <p className="success-message">{message}</p>}
      </div>
    </>

  );
};

export default AddStudent;