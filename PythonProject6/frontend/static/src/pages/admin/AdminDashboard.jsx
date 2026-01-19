import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './AdminDashboard.css'

function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="admin-dashboard">
      <nav className="admin-nav">
        <div className="nav-header">
          <h1>🏋️ FitTrack Admin</h1>
          <div className="user-info">
            <span>Admin: {user?.id}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
        <div className="nav-tabs">
          <NavLink 
            to="/admin/members" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Members
          </NavLink>
          <NavLink 
            to="/admin/trainers" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Trainers
          </NavLink>
          <NavLink 
            to="/admin/sessions" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Class Sessions
          </NavLink>
        </div>
      </nav>
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  )
}

export default AdminDashboard
