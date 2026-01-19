import React, { createContext, useState, useContext, useEffect } from 'react'

const AuthContext = createContext()

// Authentication context provider - manages user session
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null) // Current logged-in user {role, id}
  const [loading, setLoading] = useState(true) // Loading state during auth check

  // Restore user session from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('fittrack_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (e) {
        // Invalid data - remove it
        localStorage.removeItem('fittrack_user')
      }
    }
    setLoading(false)
  }, [])

  // Login user and save to localStorage
  const login = (role, id) => {
    const userData = { role, id }
    setUser(userData)
    localStorage.setItem('fittrack_user', JSON.stringify(userData))
  }

  // Logout user and clear localStorage
  const logout = () => {
    setUser(null)
    localStorage.removeItem('fittrack_user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
