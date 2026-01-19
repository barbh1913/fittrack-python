import React, { useState } from 'react'
import { apiCall, formatError } from '../utils/api'

// Member check-in page - Perform check-in and verify subscription status
function CheckinPage({ showMessage }) {
  const [statusMemberId, setStatusMemberId] = useState('') // Member ID for status check
  const [checkinMemberId, setCheckinMemberId] = useState('') // Member ID for check-in
  const [checkinResult, setCheckinResult] = useState(null) // Check-in result (APPROVED/DENIED)

  // Handle subscription status check (placeholder - would need separate endpoint)
  const handleCheckStatus = async (e) => {
    e.preventDefault()
    // Note: This would require a new endpoint - for now show a message
    showMessage('Use the check-in button below to verify subscription status during check-in.', 'success')
  }

  // Handle member check-in at reception desk
  const handleCheckin = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall('/checkin', 'POST', { member_id: checkinMemberId })
      setCheckinResult(result)
      if (result.result === 'APPROVED') {
        showMessage('Check-in successful!', 'success')
      }
    } catch (error) {
      setCheckinResult({ result: 'DENIED', reason: formatError(error) })
      showMessage(formatError(error))
    }
  }

  return (
    <div className="page">
      <h2>Member Check-in</h2>
      
      <div className="form-section">
        <h3>Check Subscription Status</h3>
        <form onSubmit={handleCheckStatus}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={statusMemberId}
            onChange={(e) => setStatusMemberId(e.target.value)}
          />
          <button type="submit">Check Status</button>
        </form>
        <div className="result-display">
          <p>Use the check-in button below to verify subscription status during check-in.</p>
        </div>
      </div>

      <div className="form-section">
        <h3>Perform Check-in</h3>
        <form onSubmit={handleCheckin}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={checkinMemberId}
            onChange={(e) => setCheckinMemberId(e.target.value)}
          />
          <button type="submit" className="btn-primary">Check In</button>
        </form>
        {checkinResult && (
          <div className={`result-display ${checkinResult.result === 'APPROVED' ? 'success' : 'error'}`}>
            {checkinResult.result === 'APPROVED' ? (
              <>
                <h4>✅ Check-in Approved!</h4>
                <p><strong>Result:</strong> {checkinResult.result}</p>
                {checkinResult.reason && <p><strong>Note:</strong> {checkinResult.reason}</p>}
              </>
            ) : (
              <>
                <h4>❌ Check-in Denied</h4>
                <p><strong>Result:</strong> {checkinResult.result}</p>
                <p><strong>Reason:</strong> {checkinResult.reason || 'Unknown'}</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default CheckinPage
