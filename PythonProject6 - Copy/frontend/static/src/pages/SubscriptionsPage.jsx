import React, { useState } from 'react'
import { apiCall, formatError } from '../utils/api'

// Subscription management page - Assign, freeze, unfreeze, and check subscription status
function SubscriptionsPage({ showMessage }) {
  // Form state for assigning subscription to member
  const [assignData, setAssignData] = useState({ member_id: '', plan_id: '', start_date: '' })
  // Form state for freezing subscription
  const [freezeData, setFreezeData] = useState({ sub_id: '', days: '' })
  // Subscription ID input for unfreeze operation
  const [unfreezeSubId, setUnfreezeSubId] = useState('')
  // Subscription ID input for status check
  const [statusSubId, setStatusSubId] = useState('')
  // Result from status check operation
  const [statusResult, setStatusResult] = useState(null)

  // Handle assign subscription to member
  const handleAssign = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        member_id: assignData.member_id,
        plan_id: assignData.plan_id
      }
      // Add start_date if provided (optional)
      if (assignData.start_date) {
        payload.start_date = assignData.start_date + ':00' // Add seconds to datetime-local format
      }
      const result = await apiCall('/subscriptions', 'POST', payload)
      showMessage(`Subscription assigned! ID: ${result.subscription_id}`, 'success')
      setAssignData({ member_id: '', plan_id: '', start_date: '' })
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle freeze subscription (temporarily disable)
  const handleFreeze = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/subscriptions/${freezeData.sub_id}/freeze`, 'POST', {
        days: parseInt(freezeData.days) // Number of days to freeze
      })
      showMessage(`Subscription frozen until: ${result.frozen_until || 'N/A'}`, 'success')
      setFreezeData({ sub_id: '', days: '' }) // Clear form
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle unfreeze subscription (reactivate)
  const handleUnfreeze = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/subscriptions/${unfreezeSubId}/unfreeze`, 'POST')
      showMessage(`Subscription unfrozen! Status: ${result.status}`, 'success')
      setUnfreezeSubId('') // Clear input
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle check subscription status
  const handleCheckStatus = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/subscriptions/${statusSubId}/status`)
      setStatusResult(result)
    } catch (error) {
      setStatusResult({ error: formatError(error) })
    }
  }

  return (
    <div className="page">
      <h2>Subscription Management</h2>
      
      <div className="form-section">
        <h3>Assign Subscription</h3>
        <form onSubmit={handleAssign}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={assignData.member_id}
            onChange={(e) => setAssignData({...assignData, member_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Plan ID"
            required
            value={assignData.plan_id}
            onChange={(e) => setAssignData({...assignData, plan_id: e.target.value})}
          />
          <input
            type="datetime-local"
            placeholder="Start Date (optional)"
            value={assignData.start_date}
            onChange={(e) => setAssignData({...assignData, start_date: e.target.value})}
          />
          <button type="submit">Assign Subscription</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Freeze Subscription</h3>
        <form onSubmit={handleFreeze}>
          <input
            type="text"
            placeholder="Subscription ID"
            required
            value={freezeData.sub_id}
            onChange={(e) => setFreezeData({...freezeData, sub_id: e.target.value})}
          />
          <input
            type="number"
            placeholder="Days to Freeze"
            required
            min="1"
            value={freezeData.days}
            onChange={(e) => setFreezeData({...freezeData, days: e.target.value})}
          />
          <button type="submit">Freeze</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Unfreeze Subscription</h3>
        <form onSubmit={handleUnfreeze}>
          <input
            type="text"
            placeholder="Subscription ID"
            required
            value={unfreezeSubId}
            onChange={(e) => setUnfreezeSubId(e.target.value)}
          />
          <button type="submit">Unfreeze</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Check Subscription Status</h3>
        <form onSubmit={handleCheckStatus}>
          <input
            type="text"
            placeholder="Subscription ID"
            required
            value={statusSubId}
            onChange={(e) => setStatusSubId(e.target.value)}
          />
          <button type="submit">Check Status</button>
        </form>
        {statusResult && (
          <div className={`result-display ${statusResult.error ? 'error' : 'success'}`}>
            {statusResult.error ? (
              <p>{statusResult.error}</p>
            ) : (
              <>
                <h4>Subscription Status</h4>
                <p>Status: <span className={`status-badge status-${statusResult.status.toLowerCase()}`}>
                  {statusResult.status}
                </span></p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SubscriptionsPage
