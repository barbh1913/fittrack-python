import React, { useState } from 'react'
import { apiCall, formatError } from '../utils/api'

// Class session management page - Create sessions, enroll members, view participants
function SessionsPage({ showMessage }) {
  // Form state for creating new session
  const [sessionData, setSessionData] = useState({
    title: '', time: '', capacity: '', trainer_id: '', status: 'OPEN'
  })
  // Form state for enrolling member in session
  const [enrollData, setEnrollData] = useState({ session_id: '', member_id: '' })
  // Form state for canceling enrollment
  const [cancelData, setCancelData] = useState({ session_id: '', member_id: '', reason: '' })
  // State for viewing session participants
  const [participantsData, setParticipantsData] = useState({ session_id: '', result: null })

  // Handle create session form submission
  const handleCreateSession = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall('/sessions', 'POST', {
        title: sessionData.title,
        starts_at: sessionData.time + ':00', // Add seconds to datetime-local format
        capacity: parseInt(sessionData.capacity),
        trainer_id: sessionData.trainer_id,
        status: sessionData.status
      })
      showMessage(`Session created! ID: ${result.session_id}`, 'success')
      setSessionData({ title: '', time: '', capacity: '', trainer_id: '', status: 'OPEN' })
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle member enrollment in session
  const handleEnroll = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/sessions/${enrollData.session_id}/enroll`, 'POST', {
        member_id: enrollData.member_id
      })
      showMessage(`Enrolled successfully! Enrollment ID: ${result.enrollment_id}`, 'success')
      setEnrollData({ session_id: '', member_id: '' }) // Clear form
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle enrollment cancellation
  const handleCancel = async (e) => {
    e.preventDefault()
    try {
      await apiCall(`/sessions/${cancelData.session_id}/cancel`, 'POST', {
        member_id: cancelData.member_id,
        cancel_reason: cancelData.reason || null // Optional reason
      })
      showMessage('Enrollment canceled successfully!', 'success')
      setCancelData({ session_id: '', member_id: '', reason: '' }) // Clear form
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle view participants request
  const handleViewParticipants = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/sessions/${participantsData.session_id}/participants`)
      setParticipantsData({ ...participantsData, result })
    } catch (error) {
      setParticipantsData({ ...participantsData, result: { error: formatError(error) } })
    }
  }

  return (
    <div className="page">
      <h2>Class Sessions</h2>
      
      <div className="form-section">
        <h3>Create Class Session</h3>
        <form onSubmit={handleCreateSession}>
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
          <button type="submit">Create Session</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Enroll in Class</h3>
        <form onSubmit={handleEnroll}>
          <input
            type="text"
            placeholder="Session ID"
            required
            value={enrollData.session_id}
            onChange={(e) => setEnrollData({...enrollData, session_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Member ID"
            required
            value={enrollData.member_id}
            onChange={(e) => setEnrollData({...enrollData, member_id: e.target.value})}
          />
          <button type="submit">Enroll</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Cancel Enrollment</h3>
        <form onSubmit={handleCancel}>
          <input
            type="text"
            placeholder="Session ID"
            required
            value={cancelData.session_id}
            onChange={(e) => setCancelData({...cancelData, session_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Member ID"
            required
            value={cancelData.member_id}
            onChange={(e) => setCancelData({...cancelData, member_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Cancel Reason (optional)"
            value={cancelData.reason}
            onChange={(e) => setCancelData({...cancelData, reason: e.target.value})}
          />
          <button type="submit">Cancel Enrollment</button>
        </form>
      </div>

      <div className="form-section">
        <h3>View Participants</h3>
        <form onSubmit={handleViewParticipants}>
          <input
            type="text"
            placeholder="Session ID"
            required
            value={participantsData.session_id}
            onChange={(e) => setParticipantsData({...participantsData, session_id: e.target.value})}
          />
          <button type="submit">View Participants</button>
        </form>
        {participantsData.result && (
          <div className={`result-display ${participantsData.result.error ? 'error' : 'success'}`}>
            {participantsData.result.error ? (
              <p>{participantsData.result.error}</p>
            ) : participantsData.result.participants && participantsData.result.participants.length > 0 ? (
              <>
                <h4>Participants:</h4>
                {participantsData.result.participants.map((p, idx) => (
                  <div key={idx} className="participant-item">
                    <strong>{p.full_name || 'N/A'}</strong> (ID: {p.member_id})<br />
                    Status: <span className={`status-badge status-${p.status.toLowerCase()}`}>{p.status}</span>
                  </div>
                ))}
              </>
            ) : (
              <p>No participants found.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SessionsPage
