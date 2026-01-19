import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './TrainerDashboard.css'

function TrainerDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="trainer-dashboard">
      <nav className="trainer-nav">
        <div className="nav-header">
          <h1>🏋️ FitTrack Trainer</h1>
          <div className="user-info">
            <span>Trainer: {user?.id}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
        <div className="nav-tabs">
          <NavLink 
            to="/trainer" 
            end
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Home
          </NavLink>
          <NavLink 
            to="/trainer/workout-plans" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Workout Plans
          </NavLink>
          <NavLink 
            to="/trainer/sessions" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Sessions
          </NavLink>
          <NavLink 
            to="/trainer/member-view" 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Member View
          </NavLink>
        </div>
      </nav>
      <main className="trainer-content">
        <Outlet />
      </main>
    </div>
  )
}

export default TrainerDashboard
