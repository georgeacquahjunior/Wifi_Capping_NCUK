import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import AddStudent from './pages/AddStudent';
import AddAdmin from './pages/AddAdmin';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Users from './pages/Users';
import ProtectedRoute from './routes/ProtectedRoute';
import Layout from './components/Layout';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Route */}
        <Route path="/" element={<Login />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<AdminDashboard />} />
            <Route path="/add-student" element={<AddStudent />} />
            <Route path="/add-admin" element={<AddAdmin />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/users" element={<Users />} />
          </Route>
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
