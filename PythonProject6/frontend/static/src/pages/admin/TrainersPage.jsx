import React, { useState, useEffect } from 'react'
import { apiCall, formatError } from '../../utils/api'
import './TrainersPage.css'

// Validation patterns matching backend
const ID_PATTERN = /^[A-Za-z0-9]{1,15}$/  // Alphanumeric, 1-15 chars
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
const PHONE_PATTERN_IL = /^0[2-9]\d{7,8}$/
const PHONE_PATTERN_INTL = /^\+?[1-9]\d{1,14}$/
const FULLNAME_PATTERN = /^[a-zA-Z\s]{2,100}$/

function TrainersPage({ showMessage }) {
  const [trainers, setTrainers] = useState([])
  const [searchId, setSearchId] = useState('')
  const [searchResult, setSearchResult] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTrainer, setEditingTrainer] = useState(null)
  const [formData, setFormData] = useState({
    id: '', fullname: '', email: '', phone: ''
  })
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [loading, setLoading] = useState(false)
  const [loadingList, setLoadingList] = useState(false)

  useEffect(() => {
    loadAllTrainers()
  }, [])

  // Validation functions
  const validateId = (id) => {
    if (!id) return 'ID is required'
    if (!ID_PATTERN.test(id)) return 'ID must be alphanumeric, 1-15 characters'
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

  const handleFieldChange = (name, value) => {
    setFormData({ ...formData, [name]: value })
    
    if (touched[name]) {
      const error = validateField(name, value)
      setErrors({ ...errors, [name]: error })
    }
  }

  const handleFieldBlur = (name) => {
    setTouched({ ...touched, [name]: true })
    const error = validateField(name, formData[name])
    setErrors({ ...errors, [name]: error })
  }

  const validateForm = () => {
    const newErrors = {}
    const fields = showCreateModal ? ['id', 'fullname', 'email', 'phone'] : ['fullname', 'email', 'phone']
    
    fields.forEach(field => {
      const error = validateField(field, formData[field])
      if (error) newErrors[field] = error
    })

    setErrors(newErrors)
    setTouched(Object.fromEntries(fields.map(f => [f, true])))
    return Object.keys(newErrors).length === 0
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchId) {
      showMessage('Please enter a Trainer ID', 'error')
      return
    }
    
    setLoading(true)
    try {
      const result = await apiCall(`/trainers/${searchId}`)
      setSearchResult(result)
      showMessage('Trainer found!', 'success')
    } catch (error) {
      setSearchResult(null)
      showMessage(formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      showMessage('Please fix validation errors', 'error')
      return
    }

    setLoading(true)
    try {
      const result = await apiCall('/trainers', 'POST', formData)
      showMessage(`Trainer created successfully! ID: ${result.id}`, 'success')
      setShowCreateModal(false)
      setFormData({ id: '', fullname: '', email: '', phone: '' })
      setErrors({})
      setTouched({})
      if (searchId === formData.id) {
        setSearchResult(result)
      }
      loadAllTrainers()
    } catch (error) {
      const errorMsg = formatError(error)
      showMessage(errorMsg)
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

  const handleEdit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      showMessage('Please fix validation errors', 'error')
      return
    }

    setLoading(true)
    try {
      const updateData = {
        fullname: formData.fullname,
        email: formData.email,
        phone: formData.phone
      }
      const result = await apiCall(`/trainers/${editingTrainer.id}`, 'PUT', updateData)
      showMessage('Trainer updated successfully!', 'success')
      setShowEditModal(false)
      setEditingTrainer(null)
      setErrors({})
      setTouched({})
      if (searchResult && searchResult.id === editingTrainer.id) {
        setSearchResult({ ...searchResult, ...updateData })
      }
      loadAllTrainers()
    } catch (error) {
      const errorMsg = formatError(error)
      showMessage(errorMsg)
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

  const openEditModal = (trainer) => {
    setEditingTrainer(trainer)
    setFormData({
      id: trainer.id,
      fullname: trainer.fullname,
      email: trainer.email,
      phone: trainer.phone
    })
    setErrors({})
    setTouched({})
    setShowEditModal(true)
  }

  const loadAllTrainers = async () => {
    setLoadingList(true)
    try {
      const result = await apiCall('/trainers')
      setTrainers(result.trainers || [])
    } catch (error) {
      showMessage(formatError(error))
    } finally {
      setLoadingList(false)
    }
  }

  const closeModals = () => {
    setShowCreateModal(false)
    setShowEditModal(false)
    setEditingTrainer(null)
    setFormData({ id: '', fullname: '', email: '', phone: '' })
    setErrors({})
    setTouched({})
    loadAllTrainers()
  }

  return (
    <div className="trainers-page">
      <div className="page-header">
        <h2>Trainers Management</h2>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          + Create Trainer
        </button>
      </div>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="input-wrapper">
            <input
              type="text"
              placeholder="Search by Trainer ID"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              pattern="[A-Za-z0-9]+"
              title="Alphanumeric characters only"
              maxLength={15}
            />
            {searchId && !ID_PATTERN.test(searchId) && (
              <span className="input-hint">Must be alphanumeric, 1-15 characters</span>
            )}
          </div>
          <button type="submit" disabled={loading || !searchId}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {searchResult && (
        <div className="trainer-card">
          <div className="card-header">
            <h3>Trainer Details</h3>
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

      {/* Trainers List */}
      <div className="trainers-list-section">
        <div className="section-header">
          <h3>All Trainers ({trainers.length})</h3>
          <button onClick={loadAllTrainers} disabled={loadingList} className="btn-refresh">
            {loadingList ? 'Refreshing...' : '🔄 Refresh'}
          </button>
        </div>
        
        {loadingList ? (
          <div className="loading-message">Loading trainers...</div>
        ) : trainers.length === 0 ? (
          <div className="empty-message">No trainers found.</div>
        ) : (
          <div className="trainers-grid">
            {trainers.map((trainer) => (
              <div key={trainer.id} className="trainer-card-list">
                <div className="trainer-card-header">
                  <div className="trainer-avatar">
                    {trainer.fullname.charAt(0).toUpperCase()}
                  </div>
                  <div className="trainer-info-main">
                    <h4>{trainer.fullname}</h4>
                    <span className="trainer-id">ID: {trainer.id}</span>
                  </div>
                </div>
                <div className="trainer-details">
                  <div className="detail-row">
                    <span className="detail-icon">📧</span>
                    <span className="detail-value">{trainer.email}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-icon">📱</span>
                    <span className="detail-value">{trainer.phone}</span>
                  </div>
                </div>
                <div className="trainer-actions">
                  <button 
                    onClick={() => openEditModal(trainer)} 
                    className="btn-edit-card"
                    title="Edit trainer"
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
            <h3>Create New Trainer</h3>
            <form onSubmit={handleCreate}>
              <div className="form-field">
                <label>ID <span className="required">*</span></label>
                <input
                  type="text"
                  placeholder="TRAINER001 (alphanumeric, 1-15 chars)"
                  required
                  pattern="[A-Za-z0-9]+"
                  maxLength={15}
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
                  placeholder="John Trainer"
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
                  placeholder="john@gym.com"
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
                <button type="submit" disabled={loading || Object.keys(errors).length > 0}>
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingTrainer && (
        <div className="modal-overlay" onClick={closeModals}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Trainer</h3>
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
                  placeholder="John Trainer"
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
                  placeholder="john@gym.com"
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
                <button type="submit" disabled={loading || Object.keys(errors).length > 0}>
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

export default TrainersPage
