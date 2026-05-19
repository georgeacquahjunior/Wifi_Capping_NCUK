import React, { useState } from "react";
import "../styles/AddStudent.css";

const AddStudent = () => {
  const [formData, setFormData] = useState({
    student_id: "",
    first_name: "",
    last_name: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    // Validate required fields
    if (!formData.student_id || !formData.first_name || !formData.last_name || !formData.password) {
      setMessage(" Please fill all fields.");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch("https://wifi-capping-ncuk-1.onrender.com/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to add student");
      }

      setMessage(" Student added successfully!");
      setFormData({
        student_id: "",
        first_name: "",
        last_name: "",
        password: "",
      });
    } catch (error) {
      console.error(error);
      setMessage(`${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-student-container">
      <h2>Add New Student</h2>
      <form className="add-student-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="student_id"
          placeholder="Student ID"
          value={formData.student_id}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="first_name"
          placeholder="First Name"
          value={formData.first_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name"
          value={formData.last_name}
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

        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Add Student"}
        </button>
      </form>
      {message && <p className="success-message">{message}</p>}
    </div>
  );
};

export default AddStudent;
