import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiCall, formatError } from '../../utils/api'
import './SessionDetailsPage.css'

function SessionDetailsPage({ showMessage }) {
  const { sessionId } = useParams() // Get session ID from URL
  const navigate = useNavigate() // Navigation hook
  const [participants, setParticipants] = useState([]) // Session participants list
  const [enrollMemberId, setEnrollMemberId] = useState('') // Member ID input for enrollment
  const [cancelMemberId, setCancelMemberId] = useState('') // Member ID input for cancellation
  const [cancelReason, setCancelReason] = useState('') // Optional cancellation reason
  const [loading, setLoading] = useState(false) // Loading state

  // Load participants when session ID changes
  useEffect(() => {
    loadParticipants()
  }, [sessionId])

  // Fetch all participants for this session
  const loadParticipants = async () => {
    setLoading(true)
    try {
      const result = await apiCall(`/sessions/${sessionId}/participants`)
      setParticipants(result.participants || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  // Handle member enrollment by admin
  const handleEnroll = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiCall(`/sessions/${sessionId}/enroll`, 'POST', {
        member_id: enrollMemberId
      })
      showMessage('Member enrolled successfully!', 'success')
      setEnrollMemberId('') // Clear input
      loadParticipants() // Refresh participants list
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  // Handle enrollment cancellation by admin
  const handleCancel = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiCall(`/sessions/${sessionId}/cancel`, 'POST', {
        member_id: cancelMemberId,
        cancel_reason: cancelReason || null
      })
      showMessage('Enrollment canceled successfully!', 'success')
      setCancelMemberId('') // Clear inputs
      setCancelReason('')
      loadParticipants() // Refresh participants list
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="session-details-page">
      <div className="page-header">
        <button onClick={() => navigate('/admin/sessions')} className="back-btn">
          ← Back to Sessions
        </button>
        <h2>Session Details</h2>
        <p className="session-id">Session ID: {sessionId}</p>
      </div>

      <div className="participants-section">
        <h3>Participants</h3>
        {loading ? (
          <p>Loading...</p>
        ) : participants.length > 0 ? (
          <table className="participants-table">
            <thead>
              <tr>
                <th>Member ID</th>
                <th>Full Name</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {participants.map((p, idx) => (
                <tr key={idx}>
                  <td>{p.member_id}</td>
                  <td>{p.full_name || 'N/A'}</td>
                  <td>
                    <span className={`status-badge status-${p.status.toLowerCase()}`}>
                      {p.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No participants found.</p>
        )}
      </div>

      <div className="actions-section">
        <div className="action-card">
          <h4>Enroll Member</h4>
          <form onSubmit={handleEnroll}>
            <input
              type="text"
              placeholder="Member ID"
              required
              value={enrollMemberId}
              onChange={(e) => setEnrollMemberId(e.target.value)}
            />
            <button type="submit" disabled={loading}>Enroll</button>
          </form>
        </div>

        <div className="action-card">
          <h4>Cancel Enrollment</h4>
          <form onSubmit={handleCancel}>
            <input
              type="text"
              placeholder="Member ID"
              required
              value={cancelMemberId}
              onChange={(e) => setCancelMemberId(e.target.value)}
            />
            <input
              type="text"
              placeholder="Cancel Reason (optional)"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
            />
            <button type="submit" disabled={loading} className="btn-danger">Cancel Enrollment</button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default SessionDetailsPage
