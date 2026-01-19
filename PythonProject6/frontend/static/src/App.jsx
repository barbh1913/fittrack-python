import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import MessageDisplay from './components/MessageDisplay'

// Pages
import LoginPage from './pages/LoginPage'
import AdminDashboard from './pages/admin/AdminDashboard'
import MembersPage from './pages/admin/MembersPage'
import TrainersPage from './pages/admin/TrainersPage'
import SessionsPage from './pages/admin/SessionsPage'
import TrainerDashboard from './pages/trainer/TrainerDashboard'
import TrainerHome from './pages/trainer/TrainerHome'
import WorkoutPlansPage from './pages/trainer/WorkoutPlansPage'
import TrainerSessionsPage from './pages/trainer/TrainerSessionsPage'
import MemberDashboard from './pages/member/MemberDashboard'
import MemberHome from './pages/member/MemberHome'
import CheckinPage from './pages/member/CheckinPage'
import MemberWorkoutPlansPage from './pages/member/MemberWorkoutPlansPage'
import MemberSessionsPage from './pages/member/MemberSessionsPage'
import SessionDetailsPage from './pages/admin/SessionDetailsPage'

import './App.css'

// Wrapper component to provide showMessage function to all pages
function AppContent() {
  const [message, setMessage] = useState({ text: '', type: '' }) // Global message state

  // Display message to user (auto-hide after 5 seconds)
  const showMessage = (text, type = 'error') => {
    setMessage({ text, type })
    setTimeout(() => setMessage({ text: '', type: '' }), 5000)
  }

  return (
    <div className="app">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute requiredRole="Admin">
            <AdminDashboard />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/admin/members" replace />} />
          <Route path="members" element={<MembersPage showMessage={showMessage} />} />
          <Route path="trainers" element={<TrainersPage showMessage={showMessage} />} />
          <Route path="sessions" element={<SessionsPage showMessage={showMessage} />} />
          <Route path="sessions/:sessionId" element={<SessionDetailsPage showMessage={showMessage} />} />
        </Route>

        {/* Trainer Routes */}
        <Route path="/trainer" element={
          <ProtectedRoute requiredRole="Trainer">
            <TrainerDashboard />
          </ProtectedRoute>
        }>
          <Route index element={<TrainerHome />} />
          <Route path="workout-plans" element={<WorkoutPlansPage showMessage={showMessage} />} />
          <Route path="sessions" element={<TrainerSessionsPage showMessage={showMessage} />} />
          <Route path="member-view" element={
            <ProtectedRoute requiredRole={["Trainer", "Member"]}>
              <MemberDashboard />
            </ProtectedRoute>
          }>
            <Route index element={<MemberHome />} />
            <Route path="checkin" element={<CheckinPage showMessage={showMessage} />} />
            <Route path="workout-plans" element={<MemberWorkoutPlansPage showMessage={showMessage} />} />
            <Route path="sessions" element={<MemberSessionsPage showMessage={showMessage} />} />
          </Route>
        </Route>

        {/* Member Routes */}
        <Route path="/member" element={
          <ProtectedRoute requiredRole="Member">
            <MemberDashboard />
          </ProtectedRoute>
        }>
          <Route index element={<MemberHome />} />
          <Route path="checkin" element={<CheckinPage showMessage={showMessage} />} />
          <Route path="workout-plans" element={<MemberWorkoutPlansPage showMessage={showMessage} />} />
          <Route path="sessions" element={<MemberSessionsPage showMessage={showMessage} />} />
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
      <MessageDisplay message={message} />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
