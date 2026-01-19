import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiCall, formatError } from '../../utils/api'
import './WorkoutPlansPage.css'

function WorkoutPlansPage({ showMessage }) {
  const { user } = useAuth()
  const [memberId, setMemberId] = useState('')
  const [workoutData, setWorkoutData] = useState({ title: '' })
  const [workoutItems, setWorkoutItems] = useState([{
    exercise_name: '', sets: '', reps: '', target_weight: '', notes: ''
  }])
  const [loading, setLoading] = useState(false)

  const addWorkoutItem = () => {
    setWorkoutItems([...workoutItems, {
      exercise_name: '', sets: '', reps: '', target_weight: '', notes: ''
    }])
  }

  const removeWorkoutItem = (index) => {
    setWorkoutItems(workoutItems.filter((_, i) => i !== index))
  }

  const updateWorkoutItem = (index, field, value) => {
    const updated = [...workoutItems]
    updated[index][field] = value
    setWorkoutItems(updated)
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!memberId) {
      showMessage('Please enter Member ID')
      return
    }

    const items = workoutItems.map(item => {
      if (!item.exercise_name || !item.sets || !item.reps) {
        throw new Error('All workout items must have exercise name, sets, and reps')
      }
      return {
        exercise_name: item.exercise_name,
        sets: parseInt(item.sets),
        reps: parseInt(item.reps),
        target_weight: item.target_weight ? parseFloat(item.target_weight) : null,
        notes: item.notes || null
      }
    })

    setLoading(true)
    try {
      const result = await apiCall('/workout-plans', 'POST', {
        trainer_id: user.id,
        member_id: memberId,
        title: workoutData.title,
        items: items
      })
      showMessage(`Workout plan created! ID: ${result.workout_plan_id}`, 'success')
      setMemberId('')
      setWorkoutData({ title: '' })
      setWorkoutItems([{ exercise_name: '', sets: '', reps: '', target_weight: '', notes: '' }])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="workout-plans-page">
      <h2>Create Workout Plan</h2>
      
      <form onSubmit={handleCreate} className="workout-form">
        <div className="form-section">
          <label>Member ID</label>
          <input
            type="text"
            placeholder="Enter Member ID"
            required
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            pattern="[0-9]{9}"
          />
        </div>

        <div className="form-section">
          <label>Plan Title</label>
          <input
            type="text"
            placeholder="e.g., Upper Body - Week 1"
            required
            value={workoutData.title}
            onChange={(e) => setWorkoutData({...workoutData, title: e.target.value})}
          />
        </div>

        <div className="form-section">
          <h3>Workout Items</h3>
          {workoutItems.map((item, index) => (
            <div key={index} className="workout-item-row">
              <input
                type="text"
                placeholder="Exercise Name"
                required
                value={item.exercise_name}
                onChange={(e) => updateWorkoutItem(index, 'exercise_name', e.target.value)}
              />
              <input
                type="number"
                placeholder="Sets"
                required
                min="1"
                value={item.sets}
                onChange={(e) => updateWorkoutItem(index, 'sets', e.target.value)}
              />
              <input
                type="number"
                placeholder="Reps"
                required
                min="1"
                value={item.reps}
                onChange={(e) => updateWorkoutItem(index, 'reps', e.target.value)}
              />
              <input
                type="number"
                placeholder="Weight (optional)"
                step="0.1"
                value={item.target_weight}
                onChange={(e) => updateWorkoutItem(index, 'target_weight', e.target.value)}
              />
              <input
                type="text"
                placeholder="Notes (optional)"
                value={item.notes}
                onChange={(e) => updateWorkoutItem(index, 'notes', e.target.value)}
              />
              {workoutItems.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => removeWorkoutItem(index)}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={addWorkoutItem} className="btn-add">
            + Add Exercise
          </button>
        </div>

        <button type="submit" disabled={loading} className="btn-submit">
          {loading ? 'Creating...' : 'Create Workout Plan'}
        </button>
      </form>
    </div>
  )
}

export default WorkoutPlansPage
