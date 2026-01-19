import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

// Route protection component - ensures user is authenticated and has required role
function ProtectedRoute({ children, requiredRole }) {
  const { user, loading } = useAuth()

  // Show loading state while checking authentication
  if (loading) {
    return <div className="loading">Loading...</div>
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // Check role-based access if requiredRole is specified
  if (requiredRole) {
    // Support single role or array of roles
    const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
    if (!allowedRoles.includes(user.role)) {
      // Redirect to user's default dashboard if role doesn't match
      return <Navigate to={`/${user.role.toLowerCase()}`} replace />
    }
  }

  // User is authenticated and has required role - render protected content
  return children
}

export default ProtectedRoute
