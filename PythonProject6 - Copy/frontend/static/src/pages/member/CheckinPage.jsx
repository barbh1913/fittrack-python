import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiCall, formatError } from '../../utils/api'
import './CheckinPage.css'

function CheckinPage({ showMessage }) {
  const { user } = useAuth()
  const [checkinResult, setCheckinResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCheckin = async () => {
    setLoading(true)
    setCheckinResult(null)
    
    try {
      const result = await apiCall('/checkin', 'POST', { member_id: user.id })
      setCheckinResult(result)
      if (result.result === 'APPROVED') {
        showMessage('Check-in successful!', 'success')
      } else {
        showMessage(`Check-in ${result.result}: ${result.reason || 'Unknown reason'}`, 'error')
      }
    } catch (error) {
      setCheckinResult({ result: 'DENIED', reason: formatError(error) })
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="checkin-page">
      <div className="checkin-container">
        <h2>Gym Check-in</h2>
        <p className="member-info">Member ID: {user?.id}</p>

        <div className="checkin-button-section">
          <button
            onClick={handleCheckin}
            disabled={loading}
            className="checkin-button"
          >
            {loading ? 'Processing...' : 'Check In'}
          </button>
        </div>

        {checkinResult && (
          <div className={`checkin-result ${checkinResult.result === 'APPROVED' ? 'success' : 'error'}`}>
            {checkinResult.result === 'APPROVED' ? (
              <>
                <div className="result-icon">✅</div>
                <h3>Check-in Approved!</h3>
                <p><strong>Result:</strong> {checkinResult.result}</p>
                {checkinResult.reason && <p><strong>Note:</strong> {checkinResult.reason}</p>}
              </>
            ) : (
              <>
                <div className="result-icon">❌</div>
                <h3>Check-in Denied</h3>
                <p><strong>Result:</strong> {checkinResult.result}</p>
                <p><strong>Reason:</strong> {checkinResult.reason || 'Unknown'}</p>
              </>
            )}
          </div>
        )}

        <div className="info-box">
          <h4>Check-in Requirements</h4>
          <ul>
            <li>Active subscription</li>
            <li>Subscription not expired</li>
            <li>Subscription not frozen</li>
            <li>Remaining entries available</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default CheckinPage
