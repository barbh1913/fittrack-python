import React, { useState } from 'react'
import { apiCall, formatError } from '../utils/api'

// Member management page - Create, Get, and Update member operations
function MembersPage({ showMessage }) {
  // Form state for creating new member
  const [memberData, setMemberData] = useState({
    id: '', fullname: '', email: '', phone: ''
  })
  // Member ID input for search/get operation
  const [getMemberId, setGetMemberId] = useState('')
  // Display result from get member operation (success or error)
  const [memberDisplay, setMemberDisplay] = useState(null)
  // Form state for updating existing member
  const [updateData, setUpdateData] = useState({
    id: '', fullname: '', email: '', phone: ''
  })

  // Handle create new member form submission
  const handleCreateMember = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall('/members', 'POST', memberData)
      showMessage('Member created successfully!', 'success')
      setMemberData({ id: '', fullname: '', email: '', phone: '' })
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  // Handle get member by ID form submission
  const handleGetMember = async (e) => {
    e.preventDefault()
    try {
      const result = await apiCall(`/members/${getMemberId}`)
      setMemberDisplay({ type: 'success', data: result })
    } catch (error) {
      setMemberDisplay({ type: 'error', data: formatError(error) })
    }
  }

  // Handle update member form submission
  const handleUpdateMember = async (e) => {
    e.preventDefault()
    // Build update payload with only provided fields (all optional)
    const updatePayload = {}
    if (updateData.fullname) updatePayload.fullname = updateData.fullname
    if (updateData.email) updatePayload.email = updateData.email
    if (updateData.phone) updatePayload.phone = updateData.phone

    // Validate at least one field is provided
    if (Object.keys(updatePayload).length === 0) {
      showMessage('Please provide at least one field to update')
      return
    }

    try {
      const result = await apiCall(`/members/${updateData.id}`, 'PUT', updatePayload)
      showMessage('Member updated successfully!', 'success')
      setUpdateData({ id: '', fullname: '', email: '', phone: '' })
    } catch (error) {
      showMessage(formatError(error))
    }
  }

  return (
    <div className="page">
      <h2>Member Management</h2>
      
      <div className="form-section">
        <h3>Create New Member</h3>
        <form onSubmit={handleCreateMember}>
          <input
            type="text"
            placeholder="ID (9 digits)"
            required
            pattern="[0-9]{9}"
            value={memberData.id}
            onChange={(e) => setMemberData({...memberData, id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Full Name"
            required
            value={memberData.fullname}
            onChange={(e) => setMemberData({...memberData, fullname: e.target.value})}
          />
          <input
            type="email"
            placeholder="Email"
            required
            value={memberData.email}
            onChange={(e) => setMemberData({...memberData, email: e.target.value})}
          />
          <input
            type="tel"
            placeholder="Phone (0501234567)"
            required
            value={memberData.phone}
            onChange={(e) => setMemberData({...memberData, phone: e.target.value})}
          />
          <button type="submit">Create Member</button>
        </form>
      </div>

      <div className="form-section">
        <h3>Get Member by ID</h3>
        <form onSubmit={handleGetMember}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={getMemberId}
            onChange={(e) => setGetMemberId(e.target.value)}
          />
          <button type="submit">Get Member</button>
        </form>
        {memberDisplay && (
          <div className={`result-display ${memberDisplay.type}`}>
            {memberDisplay.type === 'success' ? (
              <>
                <h4>Member Details</h4>
                <p><strong>ID:</strong> {memberDisplay.data.id}</p>
                <p><strong>Name:</strong> {memberDisplay.data.fullname}</p>
                <p><strong>Email:</strong> {memberDisplay.data.email}</p>
                <p><strong>Phone:</strong> {memberDisplay.data.phone}</p>
              </>
            ) : (
              <p>{memberDisplay.data}</p>
            )}
          </div>
        )}
      </div>

      <div className="form-section">
        <h3>Update Member</h3>
        <form onSubmit={handleUpdateMember}>
          <input
            type="text"
            placeholder="Member ID"
            required
            value={updateData.id}
            onChange={(e) => setUpdateData({...updateData, id: e.target.value})}
          />
          <input
            type="text"
            placeholder="Full Name (optional)"
            value={updateData.fullname}
            onChange={(e) => setUpdateData({...updateData, fullname: e.target.value})}
          />
          <input
            type="email"
            placeholder="Email (optional)"
            value={updateData.email}
            onChange={(e) => setUpdateData({...updateData, email: e.target.value})}
          />
          <input
            type="tel"
            placeholder="Phone (optional)"
            value={updateData.phone}
            onChange={(e) => setUpdateData({...updateData, phone: e.target.value})}
          />
          <button type="submit">Update Member</button>
        </form>
      </div>
    </div>
  )
}

export default MembersPage
