import React, { useState } from 'react'
import { apiCall, formatError } from '../utils/api'

// Workout plan management page - Create and view personalized workout plans
function WorkoutsPage({ showMessage }) {
  // Form state for workout plan metadata
  const [workoutData, setWorkoutData] = useState({
    trainer_id: '', member_id: '', title: ''
  })
  // Array of workout items (exercises) in the plan
  const [workoutItems, setWorkoutItems] = useState([{
    exercise_name: '', sets: '', reps: '', target_weight: '', notes: ''
  }])
  // Form state for viewing existing workout plan
  const [viewData, setViewData] = useState({ member_id: '', plan_id: '' })
  // Result from view workout plan operation
  const [viewResult, setViewResult] = useState(null)

  // Add new workout item to the plan
  const addWorkoutItem = () => {
    setWorkoutItems([...workoutItems, {
      exercise_name: '', sets: '', reps: '', target_weight: '', notes: ''
    }])
  }

  // Remove workout item from the plan
  const removeWorkoutItem = (index) => {
    setWorkoutItems(workoutItems.filter((_, i) => i !== index))
  }

  // Update specific field of a workout item
  const updateWorkoutItem = (index, field, value) => {
    const updated = [...workoutItems]
    updated[index][field] = value
    setWorkoutItems(updated)
  }

  // Handle create workout plan form submission
  const handleCreateWorkout = async (e) => {
    e.preventDefault()
    // Validate and format workout items
    const items = workoutItems.map(item => {
      // Validate required fields
      if (!item.exercise_name || !item.sets || !item.reps) {
        throw new Error('All workout items must have exercise name, sets, and reps')
      }
      return {
        exercise_name: item.exercise_name,
        sets: parseInt(item.sets),
        reps: parseInt(item.reps),
        target_weight: item.target_weight ? parseFloat(item.target_weight) : null, // Optional
        notes: item.notes || null // Optional
      }
    })

    try {
      const result = await apiCall('/workout-plans', 'POST', {
        trainer_id: workoutData.trainer_id,
        member_id: workoutData.member_id,
        title: workoutData.title,
        items: items
      })
      showMessage(`Workout plan created! ID: ${result.workout_plan_id}`, 'success')
      setWorkoutData({ trainer_id: '', member_id: '', title: '' })
      setWorkoutItems([{ exercise_name: '', sets: '', reps: '', target_weight: '', notes: '' }])
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle view workout plan request
  const handleViewWorkout = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/workout-plans/members/${viewData.member_id}/${viewData.plan_id}`)
      setViewResult(result)
    } catch (error) {
      setViewResult({ error: formatError(error) })
    }
  }

  return (
    <div className="page">
      <h2>Workout Plans</h2>
      
      <div className="form-section">
        <h3>Create Workout Plan</h3>
        <form onSubmit={handleCreateWorkout}>
          <input
            type="text"
            placeholder="Trainer ID"
            required
            value={workoutData.trainer_id}
            onChange={(e) => setWorkoutData({...workoutData, trainer_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Member ID"
            required
            value={workoutData.member_id}
            onChange={(e) => setWorkoutData({...workoutData, member_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Plan Title"
            required
            value={workoutData.title}
            onChange={(e) => setWorkoutData({...workoutData, title: e.target.value})}
          />
          <div>
            <h4>Workout Items</h4>
            {workoutItems.map((item, index) => (
              <div key={index} className="workout-item">
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
                    className="btn-danger"
                    onClick={() => removeWorkoutItem(index)}
                    style={{ gridColumn: '1 / -1' }}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
          <button type="button" onClick={addWorkoutItem}>Add Item</button>
          <button type="submit">Create Plan</button>
        </form>
      </div>

      <div className="form-section">
        <h3>View Workout Plan</h3>
        <form onSubmit={handleViewWorkout}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={viewData.member_id}
            onChange={(e) => setViewData({...viewData, member_id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Plan ID"
            required
            value={viewData.plan_id}
            onChange={(e) => setViewData({...viewData, plan_id: e.target.value})}
          />
          <button type="submit">View Plan</button>
        </form>
        {viewResult && (
          <div className={`result-display ${viewResult.error ? 'error' : 'success'}`}>
            {viewResult.error ? (
              <p>{viewResult.error}</p>
            ) : (
              <>
                <h4>Workout Plan</h4>
                <p><strong>Plan ID:</strong> {viewResult.plan}</p>
                <p><strong>Items Count:</strong> {viewResult.items_count}</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default WorkoutsPage
