import React from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './MemberDashboard.css'

function MemberDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  // Determine base path: if we're in trainer/member-view, use that, otherwise use /member
  const basePath = location.pathname.startsWith('/trainer/member-view') 
    ? '/trainer/member-view' 
    : '/member'

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="member-dashboard">
      <nav className="member-nav">
        <div className="nav-header">
          <h1>🏋️ FitTrack</h1>
          <div className="user-info">
            <span>Member: {user?.id}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
        <div className="nav-tabs">
          <NavLink 
            to={basePath} 
            end
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Home
          </NavLink>
          <NavLink 
            to={`${basePath}/checkin`} 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Check-in
          </NavLink>
          <NavLink 
            to={`${basePath}/workout-plans`} 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Workout Plans
          </NavLink>
          <NavLink 
            to={`${basePath}/sessions`} 
            className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
          >
            Sessions
          </NavLink>
        </div>
      </nav>
      <main className="member-content">
        <Outlet />
      </main>
    </div>
  )
}

export default MemberDashboard
