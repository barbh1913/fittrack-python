import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './TrainerHome.css'

function TrainerHome() {
  const { user } = useAuth()

  return (
    <div className="trainer-home">
      <div className="welcome-section">
        <h2>Welcome, Trainer {user?.id}</h2>
        <p>Manage your training activities and member plans</p>
      </div>

      <div className="quick-actions">
        <Link to="/trainer/workout-plans" className="action-card">
          <div className="card-icon">💪</div>
          <h3>Workout Plans</h3>
          <p>Create and manage workout plans for members</p>
        </Link>

        <Link to="/trainer/sessions" className="action-card">
          <div className="card-icon">📅</div>
          <h3>My Sessions</h3>
          <p>View and manage your class sessions</p>
        </Link>

        <Link to="/trainer/member-view" className="action-card">
          <div className="card-icon">👥</div>
          <h3>Member View</h3>
          <p>Access member features (if you're also a member)</p>
        </Link>
      </div>

      <div className="info-section">
        <div className="info-card">
          <h3>Trainer Dashboard</h3>
          <p>As a trainer, you can create workout plans for members and manage your class sessions. You also have access to member features if you're enrolled as a member.</p>
        </div>
      </div>
    </div>
  )
}

export default TrainerHome
