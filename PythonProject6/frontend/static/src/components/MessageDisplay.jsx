import React from 'react'
import './MessageDisplay.css'

// Global message display component - shows success/error messages to user
function MessageDisplay({ message }) {
  // Don't render if no message text
  if (!message.text) return null

  // Render message with type-based styling (success/error)
  return (
    <div className={`message ${message.type}-message`}>
      {message.text}
    </div>
  )
}

export default MessageDisplay
