import { useState } from "react";
import { useNavigate } from "react-router-dom";
import '../styles/Login.css';

function Login() {
  const [admin_id, setAdmin_id] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("https://wifi-capping-ncuk-1.onrender.com/admins/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ admin_id, password }) 
      });

      const data = await response.json();
      console.log("Backend response:", data);

      if (response.ok) {
        // save token
        localStorage.setItem("token", data.token);
        navigate("/dashboard");
      } else {
        setError(data.message || data.error || "Invalid credentials");
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <h2>Admin Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Admin ID"
          value={admin_id}
          onChange={(e) => setAdmin_id(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button className="submit-button" type="submit">
          Login
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default Login;

