import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiCall, formatError } from '../../utils/api'
import './MemberWorkoutPlansPage.css'

function MemberWorkoutPlansPage({ showMessage }) {
  const { user } = useAuth()
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPlans()
  }, [user.id])

  const loadPlans = async () => {
    setLoading(true)
    try {
      const result = await apiCall(`/workout-plans/members/${user.id}`)
      setPlans(result.plans || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="member-workout-plans-page">
        <h2>My Workout Plans</h2>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="member-workout-plans-page">
      <h2>My Workout Plans</h2>

      {plans.length === 0 ? (
        <div className="info-box">
          <p>No workout plans assigned yet. Contact your trainer to get started.</p>
        </div>
      ) : (
        <div className="plans-list">
          {plans.map((planData) => (
            <div key={planData.plan.id} className="plan-card">
              <div className="plan-header">
                <h3>{planData.plan.title}</h3>
                <span className="plan-date">
                  Created: {formatDate(planData.plan.created_at)}
                </span>
              </div>

              <div className="trainer-info">
                <strong>👤 Trainer:</strong> {planData.plan.trainer_name || planData.plan.trainer_id}
              </div>

              {planData.items && planData.items.length > 0 ? (
                <div className="exercises-section">
                  <h4 className="exercises-title">
                    💪 Exercises {planData.total_items > planData.items.length && (
                      <span className="exercise-count">({planData.items.length} of {planData.total_items})</span>
                    )}
                  </h4>
                  <div className="exercises-list">
                    {planData.items.map((item, index) => (
                      <div key={item.id} className="exercise-item">
                        <div className="exercise-number">{index + 1}</div>
                        <div className="exercise-content">
                          <div className="exercise-name">
                            <strong>{item.exercise_name}</strong>
                          </div>
                          <div className="exercise-details">
                            <span className="detail-badge">{item.sets} sets</span>
                            <span className="detail-separator">×</span>
                            <span className="detail-badge">{item.reps} reps</span>
                            {item.target_weight && (
                              <>
                                <span className="detail-separator">@</span>
                                <span className="detail-badge weight">{item.target_weight} kg</span>
                              </>
                            )}
                          </div>
                          {item.notes && (
                            <div className="exercise-notes">
                              <em>💡 {item.notes}</em>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  {planData.total_items > planData.items.length && (
                    <div className="more-exercises">
                      <p>+ {planData.total_items - planData.items.length} more exercise{planData.total_items - planData.items.length > 1 ? 's' : ''} in this plan</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-exercises">
                  <p>⚠️ No exercises in this plan yet.</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MemberWorkoutPlansPage
