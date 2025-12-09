import axios from 'axios'

const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || '/api/auth'
const TIMEOUT = 30000

class AuthApiError extends Error {
  constructor(message, statusCode) {
    super(message)
    this.statusCode = statusCode
    this.name = 'AuthApiError'
  }
}

export async function register(email, password) {
  try {
    const response = await axios.post(
      `${AUTH_API_URL}/register`,
      { email, password },
      { timeout: TIMEOUT }
    )
    return response.data
  } catch (error) {
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

export async function login(email, password) {
  try {
    const response = await axios.post(
      `${AUTH_API_URL}/login`,
      { email, password },
      { timeout: TIMEOUT }
    )
    return response.data
  } catch (error) {
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

