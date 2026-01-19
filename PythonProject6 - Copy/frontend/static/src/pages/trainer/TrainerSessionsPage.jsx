import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiCall, formatError } from '../../utils/api'
import './TrainerSessionsPage.css'

function TrainerSessionsPage({ showMessage }) {
  const { user } = useAuth()
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const loadSessions = async () => {
    setRefreshing(true)
    try {
      const result = await apiCall(`/sessions/trainer/${user.id}`)
      setSessions(result.sessions || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [user.id])

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

  const isFull = (session) => {
    return session.current_participants >= session.capacity
  }

  return (
    <div className="trainer-sessions-page">
      <div className="page-header">
        <h2>My Class Sessions</h2>
        <button onClick={loadSessions} disabled={refreshing} className="btn-refresh">
          {refreshing ? 'Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="info-box">
          <p>No sessions scheduled for the next 2 weeks.</p>
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
                  <strong>👥 Participants:</strong>{' '}
                  <span className={isFull(session) ? 'full' : ''}>
                    {session.current_participants} / {session.capacity}
                  </span>
                </div>
              </div>

              <div className="session-info">
                {isFull(session) && (
                  <div className="full-warning">
                    ⚠️ Session is full
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TrainerSessionsPage
