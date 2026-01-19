import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiCall, formatError } from '../utils/api'
import './LoginPage.css'

function LoginPage() {
  const [role, setRole] = useState('Member') // Selected role (Member/Trainer/Admin)
  const [id, setId] = useState('') // User ID input
  const [error, setError] = useState('') // Login error message
  const [loading, setLoading] = useState(false) // Loading state
  const { login } = useAuth() // Auth context login function
  const navigate = useNavigate() // Navigation hook

  // Handle login form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate user exists in database based on role
      if (role === 'Member') {
        await apiCall(`/members/${id}`)
        login(role, id)
        navigate('/member')
      } else if (role === 'Trainer') {
        await apiCall(`/trainers/${id}`)
        login(role, id)
        navigate('/trainer')
      } else if (role === 'Admin') {
        await apiCall(`/admins/${id}`)
        login(role, id)
        navigate('/admin')
      }
    } catch (error) {
      setError(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>🏋️ FitTrack</h1>
        <h2>Gym Management System</h2>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            >
              <option value="Member">Member</option>
              <option value="Trainer">Trainer</option>
              <option value="Admin">Admin</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>
              {role === 'Admin' ? 'Admin ID' : role === 'Trainer' ? 'Trainer ID' : 'Member ID'}
            </label>
            <input
              type="text"
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder={`Enter ${role} ID`}
              required
              pattern={role === 'Member' ? '[0-9]{9}' : '[A-Za-z0-9]+'}
              title={role === 'Member' ? 'Must be exactly 9 digits' : 'Alphanumeric characters only'}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
