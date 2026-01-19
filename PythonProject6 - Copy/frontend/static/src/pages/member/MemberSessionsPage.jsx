import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiCall, formatError } from '../../utils/api'
import './MemberSessionsPage.css'

function MemberSessionsPage({ showMessage }) {
  const { user } = useAuth() // Get current logged-in user
  const [sessions, setSessions] = useState([]) // Weekly sessions list
  const [loading, setLoading] = useState(false) // Loading state for enroll/cancel actions
  const [refreshing, setRefreshing] = useState(false) // Loading state for session list refresh

  // Load weekly sessions for the current member
  const loadSessions = async () => {
    setRefreshing(true)
    try {
      const result = await apiCall(`/sessions/weekly?member_id=${user.id}`)
      setSessions(result.sessions || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setRefreshing(false)
    }
  }

  // Load sessions on mount and when user changes
  useEffect(() => {
    loadSessions()
  }, [user.id])

  // Auto-refresh when page becomes visible or window gains focus
  // This ensures member sees updated enrollment status when admin enrolls/cancels enrollment
  useEffect(() => {
    if (!user?.id) return

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // Immediate refresh when page becomes visible
        loadSessions()
      }
    }

    const handleFocus = () => {
      // Immediate refresh when window gains focus
      loadSessions()
    }

    // Refresh when tab becomes visible
    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    // Refresh when window gains focus (user clicks back to tab)
    window.addEventListener('focus', handleFocus)

    // Periodic auto-refresh every 10 seconds (only when page is visible)

    const refreshInterval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        loadSessions()
      }
    }, 10000) // 10 seconds - more frequent to catch admin enrollments

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('focus', handleFocus)
      clearInterval(refreshInterval)
    }
  }, [user.id])

  // Handle enrollment in a session
  const handleEnroll = async (sessionId) => {
    setLoading(true)
    try {
      await apiCall(`/sessions/${sessionId}/enroll`, 'POST', {
        member_id: user.id
      })
      showMessage('Enrolled successfully!', 'success')
      await loadSessions() // Refresh to show updated enrollment status
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  // Handle enrollment cancellation
  const handleCancel = async (sessionId) => {
    setLoading(true)
    try {
      await apiCall(`/sessions/${sessionId}/cancel`, 'POST', {
        member_id: user.id,
        cancel_reason: null
      })
      showMessage('Enrollment canceled successfully!', 'success')
      await loadSessions() // Refresh to show updated enrollment status
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  // Format ISO date string to readable format
  const formatDateTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Check if session is at full capacity
  const isFull = (session) => {
    return session.current_participants >= session.capacity
  }

  return (
    <div className="member-sessions-page">
      <div className="page-header">
        <h2>Class Sessions - This Week</h2>
        <button onClick={loadSessions} disabled={refreshing} className="btn-refresh">
          {refreshing ? 'Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="info-box">
          <p>No sessions available for this week.</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map((session) => (
            <div key={session.id} className="session-card">
              <div className="session-header">
                <h3>{session.title}</h3>
                <span className={`session-status ${session.status.toLowerCase()}`}>
                  {session.status}
                </span>
              </div>
              
              <div className="session-details">
                <div className="detail-item">
                  <strong>📅 Time:</strong> {formatDateTime(session.starts_at)}
                </div>
                <div className="detail-item">
                  <strong>👤 Trainer:</strong> {session.trainer_name || session.trainer_id}
                </div>
                <div className="detail-item">
                  <strong>👥 Participants:</strong>{' '}
                  <span className={isFull(session) ? 'full' : ''}>
                    {session.current_participants} / {session.capacity}
                  </span>
                </div>
              </div>

              <div className="session-actions">
                {session.is_enrolled ? (
                  <button
                    onClick={() => handleCancel(session.id)}
                    disabled={loading}
                    className="btn-cancel"
                  >
                    {loading ? 'Canceling...' : 'Cancel Enrollment'}
                  </button>
                ) : (
                  <button
                    onClick={() => handleEnroll(session.id)}
                    disabled={loading || isFull(session)}
                    className="btn-enroll"
                  >
                    {loading ? 'Enrolling...' : isFull(session) ? 'Full' : 'Enroll'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MemberSessionsPage
