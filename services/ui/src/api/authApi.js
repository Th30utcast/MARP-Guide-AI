import axios from 'axios'

// Authentication API endpoint - can be configured via environment variable
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || '/api/auth'
const TIMEOUT = 30000 // 30 second timeout for auth operations

/**
 * Custom error class for authentication API errors.
 * Includes HTTP status code for better error handling.
 */
class AuthApiError extends Error {
  constructor(message, statusCode) {
    super(message)
    this.statusCode = statusCode
    this.name = 'AuthApiError'
  }
}

/**
 * Registers a new user account with email and password.
 * Creates a new user in the system but does not automatically log them in.
 *
 * @param {string} email - User's email address
 * @param {string} password - User's password (hashed on backend)
 * @returns {Promise<Object>} Registration confirmation response
 * @throws {AuthApiError} If registration fails (e.g., duplicate email, invalid credentials)
 */
export async function register(email, password) {
  try {
    const response = await axios.post(
      `${AUTH_API_URL}/register`,
      { email, password },
      { timeout: TIMEOUT }
    )
    return response.data
  } catch (error) {
    // Handle different error types with user-friendly messages
    if (error.code === 'ECONNABORTED') {
      throw new AuthApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new AuthApiError('Network error. Check your connection.', 0)
    }
    throw new AuthApiError(
      error.response.data?.detail || 'Registration failed',
      error.response.status
    )
  }
}

/**
 * Authenticates a user with email and password.
 * Returns session token, user email, user ID, and admin status on success.
 *
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Object containing session_token, email, user_id, and is_admin
 * @throws {AuthApiError} If login fails (invalid credentials, account not found, etc.)
 */
export async function login(email, password) {
  try {
    const response = await axios.post(
      `${AUTH_API_URL}/login`,
      { email, password },
      { timeout: TIMEOUT }
    )
    return response.data
  } catch (error) {
    // Handle different error types with user-friendly messages
    if (error.code === 'ECONNABORTED') {
      throw new AuthApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new AuthApiError('Network error. Check your connection.', 0)
    }
    throw new AuthApiError(
      error.response.data?.detail || 'Login failed',
      error.response.status
    )
  }
}

/**
 * Logs out the current user and invalidates their session token.
 * Cleans up server-side session data.
 *
 * @param {string} token - The user's session token
 * @returns {Promise<Object>} Logout confirmation response
 * @throws {AuthApiError} If logout fails
 */
export async function logout(token) {
  try {
    const response = await axios.post(
      `${AUTH_API_URL}/logout`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
        timeout: TIMEOUT
      }
    )
    return response.data
  } catch (error) {
    // Handle different error types with user-friendly messages
    if (error.code === 'ECONNABORTED') {
      throw new AuthApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new AuthApiError('Network error. Check your connection.', 0)
    }
    throw new AuthApiError(
      error.response.data?.detail || 'Logout failed',
      error.response.status
    )
  }
}

/**
 * Validates if a session token is still valid and active.
 * Used on app load to check if user has an existing valid session.
 * Prevents stale credentials by verifying token with backend.
 *
 * @param {string} token - The session token to validate
 * @returns {Promise<Object>} Object with user details (email, user_id, is_admin) if valid
 * @throws {AuthApiError} If token is invalid, expired, or validation fails
 */
export async function validateSession(token) {
  try {
    const response = await axios.get(
      `${AUTH_API_URL}/validate`,
      {
        headers: { Authorization: `Bearer ${token}` },
        timeout: TIMEOUT
      }
    )
    return response.data
  } catch (error) {
    // Handle different error types with user-friendly messages
    if (error.code === 'ECONNABORTED') {
      throw new AuthApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new AuthApiError('Network error. Check your connection.', 0)
    }
    throw new AuthApiError(
      error.response.data?.detail || 'Session validation failed',
      error.response.status
    )
  }
}
