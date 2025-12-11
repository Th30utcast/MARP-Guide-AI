import { useState } from 'react'
import { register } from '../api/authApi'

function Register({ onRegister, onSwitchToLogin, error, setError }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isFocused, setIsFocused] = useState({ email: false, password: false, confirmPassword: false })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError('Please fill in all fields')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setIsLoading(true)
    try {
      const response = await register(email.trim(), password)
      onRegister(response)
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
      <div
        className="w-full max-w-md rounded-xl p-8 shadow-lg animate-fade-in"
        style={{
          backgroundColor: 'var(--lancaster-white)',
          boxShadow: 'var(--lancaster-shadow-lg)'
        }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: 'var(--lancaster-red)' }}
          >
            Create Account
          </h1>
          <p style={{ color: 'var(--lancaster-text-secondary)' }}>
            Sign up to start using MARP Guide AI
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div
            className="mb-6 p-4 rounded-lg flex items-center gap-3"
            style={{
              backgroundColor: '#FEE2E2',
              border: '1px solid #FCA5A5',
              color: '#991B1B'
            }}
          >
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div>
            <label
              htmlFor="reg-email"
              className="block text-sm font-semibold mb-2"
              style={{ color: 'var(--lancaster-text-primary)' }}
            >
              Email Address
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setIsFocused({ ...isFocused, email: true })}
              onBlur={() => setIsFocused({ ...isFocused, email: false })}
              placeholder="your.email@lancaster.ac.uk"
              required
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-lg border-2 focus:outline-none transition-all"
              style={{
                backgroundColor: 'var(--lancaster-bg)',
                borderColor: isFocused.email ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
                color: 'var(--lancaster-text-primary)',
                boxShadow: isFocused.email ? 'var(--lancaster-shadow-sm)' : 'none'
              }}
            />
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="reg-password"
              className="block text-sm font-semibold mb-2"
              style={{ color: 'var(--lancaster-text-primary)' }}
            >
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setIsFocused({ ...isFocused, password: true })}
              onBlur={() => setIsFocused({ ...isFocused, password: false })}
              placeholder="At least 8 characters"
              required
              minLength={8}
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-lg border-2 focus:outline-none transition-all"
              style={{
                backgroundColor: 'var(--lancaster-bg)',
                borderColor: isFocused.password ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
                color: 'var(--lancaster-text-primary)',
                boxShadow: isFocused.password ? 'var(--lancaster-shadow-sm)' : 'none'
              }}
            />
            <p className="text-xs mt-1" style={{ color: 'var(--lancaster-text-tertiary)' }}>
              Must be at least 8 characters
            </p>
          </div>

          {/* Confirm Password Field */}
          <div>
            <label
              htmlFor="reg-confirm-password"
              className="block text-sm font-semibold mb-2"
              style={{ color: 'var(--lancaster-text-primary)' }}
            >
              Confirm Password
            </label>
            <input
              id="reg-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              onFocus={() => setIsFocused({ ...isFocused, confirmPassword: true })}
              onBlur={() => setIsFocused({ ...isFocused, confirmPassword: false })}
              placeholder="Re-enter your password"
              required
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-lg border-2 focus:outline-none transition-all"
              style={{
                backgroundColor: 'var(--lancaster-bg)',
                borderColor: isFocused.confirmPassword ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
                color: 'var(--lancaster-text-primary)',
                boxShadow: isFocused.confirmPassword ? 'var(--lancaster-shadow-sm)' : 'none'
              }}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !email.trim() || !password.trim() || !confirmPassword.trim()}
            className="w-full py-3 rounded-lg font-semibold disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
            style={{
              backgroundColor: isLoading || !email.trim() || !password.trim() || !confirmPassword.trim() ? 'var(--lancaster-border)' : 'var(--lancaster-red)',
              color: isLoading || !email.trim() || !password.trim() || !confirmPassword.trim() ? 'var(--lancaster-text-tertiary)' : 'var(--lancaster-white)',
              boxShadow: isLoading || !email.trim() || !password.trim() || !confirmPassword.trim() ? 'none' : 'var(--lancaster-shadow-md)'
            }}
            onMouseEnter={(e) => {
              if (!isLoading && email.trim() && password.trim() && confirmPassword.trim()) {
                e.target.style.backgroundColor = 'var(--lancaster-red-dark)'
                e.target.style.transform = 'scale(1.02)'
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading && email.trim() && password.trim() && confirmPassword.trim()) {
                e.target.style.backgroundColor = 'var(--lancaster-red)'
                e.target.style.transform = 'scale(1)'
              }
            }}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Creating account...</span>
              </>
            ) : (
              <>
                <span>Create Account</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </>
            )}
          </button>
        </form>

        {/* Switch to Login */}
        <div className="mt-6 text-center">
          <p style={{ color: 'var(--lancaster-text-secondary)' }} className="text-sm">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="font-semibold hover:underline"
              style={{ color: 'var(--lancaster-red)' }}
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register
