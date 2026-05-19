import "../styles/Users.css";
import { useNavigate } from "react-router-dom";

function Users() {
  const navigate = useNavigate();

  return (
    <div className="users-container">
      <h2>Admin Actions</h2>

      <div className="admin-actions">
        <button onClick={() => navigate("/add-student")}>
          Add Student
        </button>
        <button onClick={() => navigate("/add-admin")}>
          Add Admin
        </button>
      </div>
    </div>
  );
}

export default Users;


