import { useState, useEffect } from 'react'
import ChatContainer from './components/ChatContainer'
import Analytics from './components/Analytics'
import Sidebar from './components/Sidebar'
import Login from './components/Login'
import Register from './components/Register'
import { logout, validateSession } from './api/authApi'
import { resetAnalytics } from './api/analyticsApi'
import lancasterLogo from '/LancasterLogo.png'

/**
 * Main App component - root of the RAG-powered chat application.
 * Handles authentication flow, session validation, and routing between chat and analytics pages.
 *
 * Key features:
 * - Session-based authentication with token validation
 * - User isolation (chat history and analytics per user)
 * - Admin users get access to global analytics
 * - Auto-validates stored credentials on app load
 */
function App() {
    // Authentication state
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [showRegister, setShowRegister] = useState(false) // Toggle between login/register forms
    const [user, setUser] = useState(null) // Current user info (email, user_id)
    const [isAdmin, setIsAdmin] = useState(false) // Admin flag for analytics access control
    const [authError, setAuthError] = useState(null) // Auth-related error messages

    // Navigation state
    const [currentPage, setCurrentPage] = useState('chat') // 'chat' or 'analytics'

    /**
     * On component mount, validates any existing session token from localStorage.
     * This prevents users from having to re-login every time they refresh the page.
     * If token is invalid/expired, clears all stored credentials for security.
     */
    useEffect(() => {
      const validateExistingSession = async () => {
        const token = localStorage.getItem('session_token')
        const userEmail = localStorage.getItem('user_email')
        const userId = localStorage.getItem('user_id')

        if (token && userEmail && userId) {
          try {
            // Validate session with backend to ensure token is still active
            const validationResult = await validateSession(token)

            // Session is valid - restore user's authenticated state
            setIsAuthenticated(true)
            setUser({ email: validationResult.email, user_id: validationResult.user_id })
            setIsAdmin(validationResult.is_admin || false)
          } catch (error) {
            // Session invalid or expired - clear all localStorage for security
            console.log('Session validation failed, clearing stored credentials')
            localStorage.removeItem('session_token')
            localStorage.removeItem('user_email')
            localStorage.removeItem('user_id')
            localStorage.removeItem('selectedModel')
            localStorage.removeItem('comparisonShown')
            localStorage.removeItem('chatMessages')
            localStorage.removeItem('queryCount')
            setIsAuthenticated(false)
            setUser(null)
          }
        }
      }

      validateExistingSession()
    }, [])

    /**
     * Handles successful login response from authentication API.
     * Stores session token and user info in localStorage, updates app state.
     *
     * @param {Object} response - Login response containing session_token, email, user_id, is_admin
     */
    const handleLogin = (response) => {
      localStorage.setItem('session_token', response.session_token)
      localStorage.setItem('user_email', response.email)
      localStorage.setItem('user_id', response.user_id)
      setIsAuthenticated(true)
      setUser({ email: response.email, user_id: response.user_id })
      setIsAdmin(response.is_admin || false)
      setAuthError(null)
    }

    /**
     * Handles successful registration.
     * Switches back to login form and prompts user to sign in.
     *
     * @param {Object} response - Registration confirmation response
     */
    const handleRegister = (response) => {
      setAuthError(null)
      setShowRegister(false)
      alert('Registration successful! Please sign in with your credentials.')
    }

    /**
     * Logs out the current user.
     * Calls backend logout endpoint, then clears all localStorage data including:
     * - Authentication tokens
     * - Chat history (for user isolation)
     * - Model preferences
     */
    const handleLogout = async () => {
      try {
        const token = localStorage.getItem('session_token')
        if (token) {
          await logout(token) // Invalidate session on backend
        }
      } catch (err) {
        console.error('Logout error:', err)
      } finally {
        // Clear auth data
        localStorage.removeItem('session_token')
        localStorage.removeItem('user_email')
        localStorage.removeItem('user_id')
        // Clear chat data for user isolation (prevent next user from seeing previous user's data)
        localStorage.removeItem('selectedModel')
        localStorage.removeItem('comparisonShown')
        localStorage.removeItem('chatMessages')
        localStorage.removeItem('queryCount')
        setIsAuthenticated(false)
        setUser(null)
        setIsAdmin(false)
      }
    }

    /**
     * Resets all application data including chat history and analytics.
     * Admin function for testing or demo purposes.
     * Requires user confirmation before proceeding.
     */
    const handleReset = async () => {
      if (confirm('Are you sure you want to reset everything? This will clear all chat messages, model selection, and analytics data.')) {
        try {
          await resetAnalytics() // Clear backend analytics data
          // Clear frontend localStorage
          localStorage.removeItem('selectedModel')
          localStorage.removeItem('comparisonShown')
          localStorage.removeItem('chatMessages')
          localStorage.removeItem('queryCount')
          window.location.reload()
        } catch (error) {
          console.error('Error during reset:', error)
          // Even if backend reset fails, clear frontend data
          localStorage.removeItem('selectedModel')
          localStorage.removeItem('comparisonShown')
          localStorage.removeItem('chatMessages')
          localStorage.removeItem('queryCount')
          window.location.reload()
        }
      }
    }

    // Render login/register screens if user is not authenticated
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

    // Render main application interface if authenticated
    return (
      <div className="h-screen flex" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
        {/* Left sidebar with navigation, user info, and action buttons */}
        <Sidebar
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          onReset={handleReset}
          onLogout={handleLogout}
          user={user}
        />

        {/* Main content area - switches between Chat and Analytics */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div
            className="flex-1 overflow-hidden"
            style={{ backgroundColor: 'var(--lancaster-bg)' }}
          >
            {/* Conditionally render Chat or Analytics page based on navigation state */}
            {currentPage === 'chat' ? <ChatContainer /> : <Analytics isAdmin={isAdmin} />}
          </div>
        </div>
      </div>
    )
}

export default App
