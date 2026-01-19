import React from 'react'
import './Navbar.css'

function Navbar({ currentPage, setCurrentPage }) {
  const pages = [
    { id: 'members', label: 'Members' },
    { id: 'sessions', label: 'Classes' },
    { id: 'checkin', label: 'Check-in' },
    { id: 'subscriptions', label: 'Subscriptions' },
    { id: 'workouts', label: 'Workout Plans' }
  ]

  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="logo">🏋️ FitTrack</h1>
        <ul className="nav-menu">
          {pages.map(page => (
            <li key={page.id}>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  setCurrentPage(page.id)
                }}
                className={currentPage === page.id ? 'active' : ''}
              >
                {page.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  )
}

export default Navbar
