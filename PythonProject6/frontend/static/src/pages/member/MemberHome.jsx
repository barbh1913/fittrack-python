import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './MemberHome.css'

function MemberHome() {
  const { user } = useAuth()
  const location = useLocation()
  
  // Determine base path: if we're in trainer/member-view, use that, otherwise use /member
  const basePath = location.pathname.startsWith('/trainer/member-view') 
    ? '/trainer/member-view' 
    : '/member'

  return (
    <div className="member-home">
      <div className="welcome-section">
        <h2>Welcome, Member {user?.id}</h2>
        <p>Manage your gym activities from here</p>
      </div>

      <div className="quick-actions">
        <Link to={`${basePath}/checkin`} className="action-card checkin-card">
          <div className="card-icon">✓</div>
          <h3>Check In</h3>
          <p>Check in to the gym</p>
        </Link>

        <Link to={`${basePath}/workout-plans`} className="action-card">
          <div className="card-icon">💪</div>
          <h3>Workout Plans</h3>
          <p>View your workout plans</p>
        </Link>

        <Link to={`${basePath}/sessions`} className="action-card">
          <div className="card-icon">📅</div>
          <h3>Class Sessions</h3>
          <p>Enroll in classes</p>
        </Link>
      </div>

      <div className="info-section">
        <div className="info-card">
          <h3>Subscription Status</h3>
          <p>Check your subscription status when you check in</p>
        </div>
      </div>
    </div>
  )
}

export default MemberHome
