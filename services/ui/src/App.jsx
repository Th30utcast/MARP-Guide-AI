import { useState, useEffect } from 'react'
import ChatContainer from './components/ChatContainer'
<<<<<<< Updated upstream
=======
import Login from './components/Login'
import Register from './components/Register'
import { logout } from './api/authApi'
import lancasterLogo from '/LancasterLogo.png'
>>>>>>> Stashed changes

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [user, setUser] = useState(null)
  const [authError, setAuthError] = useState(null)

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('session_token')
    const userEmail = localStorage.getItem('user_email')
    const userId = localStorage.getItem('user_id')
    
    if (token && userEmail && userId) {
      setIsAuthenticated(true)
      setUser({ email: userEmail, user_id: userId })
    }
  }, [])

  const handleLogin = (response) => {
    localStorage.setItem('session_token', response.session_token)
    localStorage.setItem('user_email', response.email)
    localStorage.setItem('user_id', response.user_id)
    setIsAuthenticated(true)
    setUser({ email: response.email, user_id: response.user_id })
    setAuthError(null)
  }

  const handleRegister = (response) => {
    // After registration, show success message and switch to login
    setAuthError(null)
    setShowRegister(false)
    // Show a message that they can now login
    alert('Registration successful! Please sign in with your credentials.')
  }

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('session_token')
      if (token) {
        await logout(token)
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      localStorage.removeItem('session_token')
      localStorage.removeItem('user_email')
      localStorage.removeItem('user_id')
      setIsAuthenticated(false)
      setUser(null)
    }
  }

  // Show login/register if not authenticated
  if (!isAuthenticated) {
    return showRegister ? (
      <Register
        onRegister={handleRegister}
        onSwitchToLogin={() => {
          setShowRegister(false)
          setAuthError(null)
        }}
        error={authError}
        setError={setAuthError}
      />
    ) : (
      <Login
        onLogin={handleLogin}
        onSwitchToRegister={() => {
          setShowRegister(true)
          setAuthError(null)
        }}
        error={authError}
        setError={setAuthError}
      />
    )
  }

  // Show main app if authenticated
  return (
<<<<<<< Updated upstream
    <div className="min-h-screen" style={{ backgroundColor: '#2b2d31' }}>
      <header className="border-b px-4 py-3" style={{ backgroundColor: '#1e1f22', borderColor: '#3f4147' }}>
        <h1 className="text-xl font-semibold text-gray-100">
          MARP Guide AI
        </h1>
        <p className="text-sm text-gray-400">Ask questions about Lancaster's MARP</p>
=======
    <div className="min-h-screen" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
      <header
        className="border-b px-6 py-4 backdrop-blur-sm"
        style={{
          backgroundColor: 'var(--lancaster-white)',
          borderColor: 'var(--lancaster-border)',
          boxShadow: 'var(--lancaster-shadow-sm)'
        }}
      >
        <div className="container mx-auto max-w-5xl flex items-center gap-4">
          {/* Lancaster Logo */}
          <img
            src={lancasterLogo}
            alt="Lancaster University"
            className="h-12 w-auto object-contain"
            style={{ filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))' }}
          />

          {/* Divider */}
          <div
            className="h-10 w-px"
            style={{ backgroundColor: 'var(--lancaster-border)' }}
          />

          {/* Title Section */}
          <div className="flex-1">
            <h1
              className="text-2xl font-bold tracking-tight"
              style={{ color: 'var(--lancaster-red)' }}
            >
              MARP Guide AI
            </h1>
            <p
              className="text-sm"
              style={{ color: 'var(--lancaster-text-secondary)' }}
            >
              Your intelligent assistant for Lancaster's Manual of Academic Regulations and Procedures
            </p>
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-semibold" style={{ color: 'var(--lancaster-text-primary)' }}>
                {user?.email}
              </p>
              <p className="text-xs" style={{ color: 'var(--lancaster-text-tertiary)' }}>
                Signed in
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all"
              style={{
                backgroundColor: 'var(--lancaster-white)',
                color: 'var(--lancaster-red)',
                border: '1px solid var(--lancaster-red)'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'var(--lancaster-red)'
                e.target.style.color = 'var(--lancaster-white)'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'var(--lancaster-white)'
                e.target.style.color = 'var(--lancaster-red)'
              }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>

          {/* Beta Badge */}
          <div
            className="px-3 py-1 rounded-full text-xs font-semibold"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              color: 'var(--lancaster-white)'
            }}
          >
            BETA
          </div>
        </div>
>>>>>>> Stashed changes
      </header>
      <main className="container mx-auto max-w-4xl h-[calc(100vh-80px)]">
        <ChatContainer />
      </main>
    </div>
  )
}

export default App
