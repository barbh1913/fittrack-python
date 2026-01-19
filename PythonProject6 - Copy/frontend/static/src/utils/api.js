// Base API URL - all endpoints are prefixed with /api
const API_BASE = '/api'

/**
 * Format error object into user-friendly string message
 * @param {Object|string} error - Error object or string
 * @returns {string} Formatted error message
 */
export function formatError(error) {
  if (typeof error === 'string') return error
  if (error.error) return error.error
  if (error.details) return JSON.stringify(error.details, null, 2)
  if (error.message) return error.message
  return 'An unknown error occurred'
}

/**
 * Make API call to backend
 * @param {string} endpoint - API endpoint (e.g., '/members')
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {Object} body - Request body data (for POST/PUT)
 * @returns {Promise<Object>} API response data
 */
export async function apiCall(endpoint, method = 'GET', body = null) {
  try {
    // Prepare request options
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      }
    }
    
    // Add request body for POST/PUT requests
    if (body) {
      options.body = JSON.stringify(body)
    }
    
    // Make HTTP request
    const response = await fetch(`${API_BASE}${endpoint}`, options)
    
    // Check for network errors
    if (!response) {
      throw {
        error: 'Network error: No response from server',
        details: 'Make sure Flask server is running on http://localhost:5000'
      }
    }
    
    // Read response text (can only read body once)
    const text = await response.text()
    
    // Handle empty response
    if (!text || text.trim() === '') {
      throw {
        error: 'Empty response from server',
        details: `Flask server may not be running. Start it with: py run.py\nStatus: ${response.status} ${response.statusText}`
      }
    }
    
    // Verify response is JSON (not HTML error page)
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      throw {
        error: `Server returned non-JSON response (${response.status} ${response.statusText})`,
        details: text.substring(0, 200) // First 200 chars for debugging
      }
    }
    
    // Parse JSON response
    let data
    try {
      data = JSON.parse(text)
    } catch (parseError) {
      throw {
        error: 'Invalid JSON response from server',
        details: parseError.message
      }
    }
    
    // Throw error if response status is not OK
    if (!response.ok) {
      throw data
    }
    
    return data
  } catch (error) {
    // Re-throw formatted errors, wrap others
    if (error.error || error.details) {
      throw error
    }
    throw { error: 'Network error: ' + error.message }
  }
}
