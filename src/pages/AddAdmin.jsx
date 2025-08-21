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

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // TODO: Replace this with an actual API call
    console.log("New admin submitted:", formData);

    setMessage("Admin added successfully!");
    setFormData({
      admin_id: "",
      firstName: "",
      lastName: "",
      password: "",
    });
  };

  return (
    <>
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
      </div>
    </>

  );
};

export default AddAdmin;
