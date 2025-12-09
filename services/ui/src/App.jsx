  import { useState, useEffect } from 'react'
  import ChatContainer from './components/ChatContainer'
  import Analytics from './components/Analytics'
  import Sidebar from './components/Sidebar'
  import Login from './components/Login'
  import Register from './components/Register'
  import { logout } from './api/authApi'
  import { resetAnalytics } from './api/analyticsApi'
  import lancasterLogo from '/LancasterLogo.png'

  function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [showRegister, setShowRegister] = useState(false)
    const [user, setUser] = useState(null)
    const [authError, setAuthError] = useState(null)
    const [currentPage, setCurrentPage] = useState('chat')

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
      setAuthError(null)
      setShowRegister(false)
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

    const handleReset = async () => {
      if (confirm('Are you sure you want to reset everything? This will clear all chat messages, model selection, and analytics
   data.')) {
        try {
          await resetAnalytics()
          localStorage.removeItem('selectedModel')
          localStorage.removeItem('comparisonShown')
          window.location.reload()
        } catch (error) {
          console.error('Error during reset:', error)
          localStorage.removeItem('selectedModel')
          localStorage.removeItem('comparisonShown')
          window.location.reload()
        }
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
      <div className="h-screen flex" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
        <Sidebar
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          onReset={handleReset}
          onLogout={handleLogout}
          user={user}
        />

        <div className="flex-1 flex flex-col overflow-hidden">
          <div
            className="flex-1 overflow-hidden"
            style={{ backgroundColor: 'var(--lancaster-bg)' }}
          >
            {currentPage === 'chat' ? <ChatContainer /> : <Analytics />}
          </div>
        </div>
      </div>
    )
  }

  export default App