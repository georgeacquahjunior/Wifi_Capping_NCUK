import React, { useState } from "react";
import "../styles/AddAdmin.css";

const AddAdmin = () => {
  const [formData, setFormData] = useState({
    admin_id: "",
    firstName: "",
    lastName: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await fetch("https://wifi-capping-ncuk-1.onrender.com/admins", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          admin_id: formData.admin_id,
          first_name: formData.firstName,
          last_name: formData.lastName,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to add admin");
      }

      setMessage(" Admin added successfully!");
      setFormData({
        admin_id: "",
        firstName: "",
        lastName: "",
        password: "",
      });
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Something went wrong");
    }
  };

  return (
    <div className="add-admin-container">
      <h2>Add New Admin</h2>

      <form onSubmit={handleSubmit} className="add-admin-form">
        <input
          type="text"
          name="admin_id"
          placeholder="Admin ID"
          value={formData.admin_id}
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

        <button type="submit">Add Admin</button>
      </form>

      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default AddAdmin;
