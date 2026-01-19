import React, { useState, useEffect } from 'react'
import { apiCall, formatError } from '../../utils/api'
import './MembersPage.css'

// Validation patterns matching backend
const ID_PATTERN = /^\d{9}$/
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
const PHONE_PATTERN_IL = /^0[2-9]\d{7,8}$/
const PHONE_PATTERN_INTL = /^\+?[1-9]\d{1,14}$/
const FULLNAME_PATTERN = /^[a-zA-Z\s]{2,100}$/

function MembersPage({ showMessage }) {
  // Component state management
  const [members, setMembers] = useState([]) // All members list
  const [searchId, setSearchId] = useState('') // Search input value
  const [searchResult, setSearchResult] = useState(null) // Single member search result
  const [showCreateModal, setShowCreateModal] = useState(false) // Create modal visibility
  const [showEditModal, setShowEditModal] = useState(false) // Edit modal visibility
  const [editingMember, setEditingMember] = useState(null) // Member being edited
  const [formData, setFormData] = useState({
    id: '', fullname: '', email: '', phone: ''
  }) // Form input values
  const [errors, setErrors] = useState({}) // Field validation errors
  const [touched, setTouched] = useState({}) // Track which fields were interacted with
  const [loading, setLoading] = useState(false) // Loading state for form actions
  const [loadingList, setLoadingList] = useState(false) // Loading state for member list

  // Load all members on component mount
  useEffect(() => {
    loadAllMembers()
  }, [])

  // Validation functions
  const validateId = (id) => {
    if (!id) return 'ID is required'
    if (!ID_PATTERN.test(id)) return 'ID must be exactly 9 digits'
    return null
  }

  const validateFullname = (name) => {
    if (!name) return 'Name is required'
    if (!FULLNAME_PATTERN.test(name)) return 'Name must be 2-100 characters, letters and spaces only'
    if (name.trim().length < 2) return 'Name must be at least 2 characters long'
    return null
  }

  const validateEmail = (email) => {
    if (!email) return 'Email is required'
    if (!EMAIL_PATTERN.test(email)) return 'Invalid email format (e.g., user@example.com)'
    return null
  }

  const validatePhone = (phone) => {
    if (!phone) return 'Phone is required'
    if (!PHONE_PATTERN_IL.test(phone) && !PHONE_PATTERN_INTL.test(phone)) {
      return 'Invalid phone format'
    }
    return null
  }

  const validateField = (name, value) => {
    switch (name) {
      case 'id':
        return validateId(value)
      case 'fullname':
        return validateFullname(value)
      case 'email':
        return validateEmail(value)
      case 'phone':
        return validatePhone(value)
      default:
        return null
    }
  }

  // Handle input field changes - validate if field was previously touched
  const handleFieldChange = (name, value) => {
    setFormData({ ...formData, [name]: value })
    
    // Only validate on change if user has already interacted with the field
    if (touched[name]) {
      const error = validateField(name, value)
      setErrors({ ...errors, [name]: error })
    }
  }

  // Handle field blur - mark as touched and validate
  const handleFieldBlur = (name) => {
    setTouched({ ...touched, [name]: true })
    const error = validateField(name, formData[name])
    setErrors({ ...errors, [name]: error })
  }

  // Validate entire form - returns true if valid, false otherwise
  const validateForm = () => {
    const newErrors = {}
    // Create form includes ID, edit form doesn't
    const fields = showCreateModal ? ['id', 'fullname', 'email', 'phone'] : ['fullname', 'email', 'phone']
    
    // Validate each field and collect errors
    fields.forEach(field => {
      const error = validateField(field, formData[field])
      if (error) newErrors[field] = error
    })

    setErrors(newErrors)
    setTouched(Object.fromEntries(fields.map(f => [f, true])))
    return Object.keys(newErrors).length === 0 // Form is valid if no errors
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchId) {
      showMessage('Please enter a Member ID', 'error')
      return
    }
    
    if (!ID_PATTERN.test(searchId)) {
      showMessage('Invalid ID format. Must be exactly 9 digits.', 'error')
      return
    }
    
    setLoading(true)
    try {
      const result = await apiCall(`/members/${searchId}`)
      setSearchResult(result)
      showMessage('Member found!', 'success')
    } catch (error) {
      setSearchResult(null)
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  // Handle create member form submission
  const handleCreate = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Validate form before submission
    if (!validateForm()) {
      showMessage('Please fix validation errors', 'error')
      return
    }

    setLoading(true)
    try {
      // Create new member via API
      const result = await apiCall('/members', 'POST', formData)
      
      // API returns {success: true, id: ..., fullname: ..., email: ..., phone: ...}
      const memberId = result.id || formData.id
      showMessage(`Member created successfully! ID: ${memberId}`, 'success')
      
      // Reset form and close modal
      setShowCreateModal(false)
      setFormData({ id: '', fullname: '', email: '', phone: '' })
      setErrors({})
      setTouched({})
      
      // Update search result if the created member matches current search
      if (searchId === formData.id) {
        setSearchResult(result)
      }
      loadAllMembers() // Refresh members list
    } catch (error) {
      const errorMsg = formatError(error)
      showMessage(errorMsg)
      
      // Parse and display field-specific validation errors from API
      if (errorMsg.includes('Validation error') || errorMsg.includes('Invalid')) {
        const errorDetails = typeof error === 'object' && error.details ? error.details : null
        if (errorDetails && Array.isArray(errorDetails)) {
          const fieldErrors = {}
          errorDetails.forEach(err => {
            if (err.loc && err.loc.length > 1) {
              const field = err.loc[err.loc.length - 1]
              fieldErrors[field] = err.msg || 'Invalid value'
            }
          })
          setErrors({ ...errors, ...fieldErrors })
        }
      }
    } finally {
      setLoading(false)
    }
  }

  // Handle edit member form submission
  const handleEdit = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Validate form before submission
    if (!validateForm()) {
      showMessage('Please fix validation errors', 'error')
      return
    }

    setLoading(true)
    try {
      // Prepare update data (ID cannot be changed)
      const updateData = {
        fullname: formData.fullname,
        email: formData.email,
        phone: formData.phone
      }
      
      // Update member via API
      const result = await apiCall(`/members/${editingMember.id}`, 'PUT', updateData)
      showMessage('Member updated successfully!', 'success')
      
      // Reset form and close modal
      setShowEditModal(false)
      setEditingMember(null)
      setFormData({ id: '', fullname: '', email: '', phone: '' })
      setErrors({})
      setTouched({})
      
      // Update search result if the edited member matches current search
      if (searchResult && searchResult.id === editingMember.id) {
        setSearchResult({ ...searchResult, ...updateData })
      }
      loadAllMembers() // Refresh members list
    } catch (error) {
      const errorMsg = formatError(error)
      showMessage(errorMsg)
      
      // Parse and display field-specific validation errors from API
      if (errorMsg.includes('Validation error') || errorMsg.includes('Invalid')) {
        const errorDetails = typeof error === 'object' && error.details ? error.details : null
        if (errorDetails && Array.isArray(errorDetails)) {
          const fieldErrors = {}
          errorDetails.forEach(err => {
            if (err.loc && err.loc.length > 1) {
              const field = err.loc[err.loc.length - 1]
              fieldErrors[field] = err.msg || 'Invalid value'
            }
          })
          setErrors({ ...errors, ...fieldErrors })
        }
      }
    } finally {
      setLoading(false)
    }
  }

  // Open edit modal and populate form with member data
  const openEditModal = (member) => {
    setEditingMember(member)
    setFormData({
      id: member.id,
      fullname: member.fullname,
      email: member.email,
      phone: member.phone
    })
    setErrors({})
    setTouched({})
    setShowEditModal(true)
  }

  // Load all members from API
  const loadAllMembers = async () => {
    setLoadingList(true)
    try {
      const result = await apiCall('/members')
      setMembers(result.members || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoadingList(false)
    }
  }

  const closeModals = () => {
    setShowCreateModal(false)
    setShowEditModal(false)
    setEditingMember(null)
    setFormData({ id: '', fullname: '', email: '', phone: '' })
    setErrors({})
    setTouched({})
    loadAllMembers() // Refresh list after closing modal
  }

  return (
    <div className="members-page">
      <div className="page-header">
        <h2>Members Management</h2>
        <button 
          onClick={() => {
            setFormData({ id: '', fullname: '', email: '', phone: '' })
            setErrors({})
            setTouched({})
            setShowCreateModal(true)
          }} 
          className="btn-primary"
        >
          + Create Member
        </button>
      </div>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="input-wrapper">
            <input
              type="text"
              placeholder="Search by Member ID (9 digits)"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              pattern="[0-9]{9}"
              title="Must be exactly 9 digits"
              maxLength={9}
            />
            {searchId && !ID_PATTERN.test(searchId) && (
              <span className="input-hint">Must be exactly 9 digits</span>
            )}
          </div>
          <button type="submit" disabled={loading || !searchId}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {searchResult && (
        <div className="member-card">
          <div className="card-header">
            <h3>Member Details</h3>
            <button onClick={() => openEditModal(searchResult)} className="btn-edit">
              Edit
            </button>
          </div>
          <div className="card-content">
            <p><strong>ID:</strong> {searchResult.id}</p>
            <p><strong>Name:</strong> {searchResult.fullname}</p>
            <p><strong>Email:</strong> {searchResult.email}</p>
            <p><strong>Phone:</strong> {searchResult.phone}</p>
          </div>
        </div>
      )}

      {/* Members List */}
      <div className="members-list-section">
        <div className="section-header">
          <h3>All Members ({members.length})</h3>
          <button onClick={loadAllMembers} disabled={loadingList} className="btn-refresh">
            {loadingList ? 'Refreshing...' : '🔄 Refresh'}
          </button>
        </div>
        
        {loadingList ? (
          <div className="loading-message">Loading members...</div>
        ) : members.length === 0 ? (
          <div className="empty-message">No members found.</div>
        ) : (
          <div className="members-grid">
            {members.map((member) => (
              <div key={member.id} className="member-card-list">
                <div className="member-card-header">
                  <div className="member-avatar">
                    {member.fullname.charAt(0).toUpperCase()}
                  </div>
                  <div className="member-info-main">
                    <h4>{member.fullname}</h4>
                    <span className="member-id">ID: {member.id}</span>
                  </div>
                </div>
                <div className="member-details">
                  <div className="detail-row">
                    <span className="detail-icon">📧</span>
                    <span className="detail-value">{member.email}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-icon">📱</span>
                    <span className="detail-value">{member.phone}</span>
                  </div>
                </div>
                <div className="member-actions">
                  <button 
                    onClick={() => openEditModal(member)} 
                    className="btn-edit-card"
                    title="Edit member"
                  >
                    ✏️ Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create New Member</h3>
            <form onSubmit={handleCreate}>
              <div className="form-field">
                <label>ID <span className="required">*</span></label>
                <input
                  type="text"
                  placeholder="123456789 (9 digits)"
                  required
                  pattern="[0-9]{9}"
                  maxLength={9}
                  value={formData.id}
                  onChange={(e) => handleFieldChange('id', e.target.value)}
                  onBlur={() => handleFieldBlur('id')}
                  className={errors.id ? 'error' : ''}
                />
                {errors.id && <span className="error-message">{errors.id}</span>}
                {!errors.id && touched.id && <span className="success-indicator">✓</span>}
              </div>

              <div className="form-field">
                <label>Full Name <span className="required">*</span></label>
                <input
                  type="text"
                  placeholder="John Doe"
                  required
                  maxLength={100}
                  value={formData.fullname}
                  onChange={(e) => handleFieldChange('fullname', e.target.value)}
                  onBlur={() => handleFieldBlur('fullname')}
                  className={errors.fullname ? 'error' : ''}
                />
                {errors.fullname && <span className="error-message">{errors.fullname}</span>}
                {!errors.fullname && touched.fullname && <span className="success-indicator">✓</span>}
              </div>

              <div className="form-field">
                <label>Email <span className="required">*</span></label>
                <input
                  type="email"
                  placeholder="john@example.com"
                  required
                  maxLength={100}
                  value={formData.email}
                  onChange={(e) => handleFieldChange('email', e.target.value)}
                  onBlur={() => handleFieldBlur('email')}
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
                {!errors.email && touched.email && <span className="success-indicator">✓</span>}
              </div>

              <div className="form-field">
                <label>Phone <span className="required">*</span></label>
                <input
                  type="tel"
                  placeholder="0501234567 or +1234567890"
                  required
                  maxLength={15}
                  value={formData.phone}
                  onChange={(e) => handleFieldChange('phone', e.target.value)}
                  onBlur={() => handleFieldBlur('phone')}
                  className={errors.phone ? 'error' : ''}
                />
                {errors.phone && <span className="error-message">{errors.phone}</span>}
                {!errors.phone && touched.phone && <span className="success-indicator">✓</span>}
              </div>

              <div className="modal-actions">
                <button type="button" onClick={closeModals}>Cancel</button>
                <button 
                  type="submit" 
                  disabled={loading || Object.keys(errors).filter(k => errors[k]).length > 0}
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingMember && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Member</h3>
            <form onSubmit={handleEdit}>
              <div className="form-field">
                <label>ID</label>
                <input
                  type="text"
                  value={formData.id}
                  disabled
                  className="disabled-input"
                />
                <span className="field-hint">ID cannot be changed</span>
              </div>

              <div className="form-field">
                <label>Full Name <span className="required">*</span></label>
                <input
                  type="text"
                  placeholder="John Doe"
                  required
                  maxLength={100}
                  value={formData.fullname}
                  onChange={(e) => handleFieldChange('fullname', e.target.value)}
                  onBlur={() => handleFieldBlur('fullname')}
                  className={errors.fullname ? 'error' : ''}
                />
                {errors.fullname && <span className="error-message">{errors.fullname}</span>}
                {!errors.fullname && touched.fullname && <span className="success-indicator">✓</span>}
              </div>

              <div className="form-field">
                <label>Email <span className="required">*</span></label>
                <input
                  type="email"
                  placeholder="john@example.com"
                  required
                  maxLength={100}
                  value={formData.email}
                  onChange={(e) => handleFieldChange('email', e.target.value)}
                  onBlur={() => handleFieldBlur('email')}
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
                {!errors.email && touched.email && <span className="success-indicator">✓</span>}
              </div>

              <div className="form-field">
                <label>Phone <span className="required">*</span></label>
                <input
                  type="tel"
                  placeholder="0501234567 or +1234567890"
                  required
                  maxLength={15}
                  value={formData.phone}
                  onChange={(e) => handleFieldChange('phone', e.target.value)}
                  onBlur={() => handleFieldBlur('phone')}
                  className={errors.phone ? 'error' : ''}
                />
                {errors.phone && <span className="error-message">{errors.phone}</span>}
                {!errors.phone && touched.phone && <span className="success-indicator">✓</span>}
              </div>

              <div className="modal-actions">
                <button type="button" onClick={closeModals}>Cancel</button>
                <button 
                  type="submit" 
                  disabled={loading || Object.keys(errors).filter(k => errors[k]).length > 0}
                >
                  {loading ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default MembersPage
