import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiCall, formatError } from '../../utils/api'
import './SessionsPage.css'

function SessionsPage({ showMessage }) {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [sessions, setSessions] = useState([])
  const [sessionData, setSessionData] = useState({
    title: '', time: '', capacity: '', trainer_id: '', status: 'OPEN'
  })
  const [loading, setLoading] = useState(false)
  const [loadingList, setLoadingList] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadAllSessions()
  }, [])

  const loadAllSessions = async () => {
    setLoadingList(true)
    try {
      const result = await apiCall('/sessions')
      setSessions(result.sessions || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoadingList(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const result = await apiCall('/sessions', 'POST', {
        title: sessionData.title,
        starts_at: sessionData.time + ':00',
        capacity: parseInt(sessionData.capacity),
        trainer_id: sessionData.trainer_id,
        status: sessionData.status
      })
      showMessage(`Session created! ID: ${result.session_id}`, 'success')
      setShowCreateModal(false)
      setSessionData({ title: '', time: '', capacity: '', trainer_id: '', status: 'OPEN' })
      loadAllSessions() // Refresh sessions list
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="sessions-page">
      <div className="page-header">
        <h2>Class Sessions Management</h2>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          + Create Session
        </button>
      </div>

      <div className="info-box">
        <p>Enter a Session ID below to view details and manage participants, or browse all sessions in the table.</p>
      </div>

      <div className="view-session-section">
        <form onSubmit={(e) => {
          e.preventDefault()
          navigate(`/admin/sessions/${sessionId}`)
        }} className="search-form">
          <input
            type="text"
            placeholder="Enter Session ID to view details"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            required
          />
          <button type="submit">View Session</button>
        </form>
      </div>

      {/* Sessions Table */}
      <div className="sessions-table-section">
        <div className="table-header">
          <h3>All Sessions ({sessions.length})</h3>
          <button onClick={loadAllSessions} disabled={loadingList} className="btn-refresh">
            {loadingList ? 'Refreshing...' : '🔄 Refresh'}
          </button>
        </div>
        
        {loadingList ? (
          <div className="loading-message">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="empty-message">No sessions found.</div>
        ) : (
          <div className="table-container">
            <table className="sessions-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Date & Time</th>
                  <th>Trainer</th>
                  <th>Participants</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td className="session-id">{session.id}</td>
                    <td className="session-title">{session.title}</td>
                    <td>{formatDateTime(session.starts_at)}</td>
                    <td>{session.trainer_name || session.trainer_id}</td>
                    <td>
                      <span className={session.current_participants >= session.capacity ? 'full' : ''}>
                        {session.current_participants} / {session.capacity}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge status-${session.status.toLowerCase()}`}>
                        {session.status}
                      </span>
                    </td>
                    <td>
                      <button 
                        onClick={() => navigate(`/admin/sessions/${session.id}`)} 
                        className="btn-view-small"
                        title="View session details"
                      >
                        👁️ View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create New Session</h3>
            <form onSubmit={handleCreate}>
              <input
                type="text"
                placeholder="Title"
                required
                value={sessionData.title}
                onChange={(e) => setSessionData({...sessionData, title: e.target.value})}
              />
              <input
                type="datetime-local"
                required
                value={sessionData.time}
                onChange={(e) => setSessionData({...sessionData, time: e.target.value})}
              />
              <input
                type="number"
                placeholder="Capacity"
                required
                min="1"
                value={sessionData.capacity}
                onChange={(e) => setSessionData({...sessionData, capacity: e.target.value})}
              />
              <input
                type="text"
                placeholder="Trainer ID"
                required
                value={sessionData.trainer_id}
                onChange={(e) => setSessionData({...sessionData, trainer_id: e.target.value})}
              />
              <select
                value={sessionData.status}
                onChange={(e) => setSessionData({...sessionData, status: e.target.value})}
              >
                <option value="OPEN">OPEN</option>
                <option value="CLOSED">CLOSED</option>
              </select>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" disabled={loading}>Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default SessionsPage
