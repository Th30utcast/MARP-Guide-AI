import axios from 'axios'

const CHAT_API_URL = import.meta.env.VITE_CHAT_API_URL || '/api/chat'
const TIMEOUT = 30000

class ChatApiError extends Error {
  constructor(message, statusCode) {
    super(message)
    this.statusCode = statusCode
    this.name = 'ChatApiError'
  }
}

export async function sendChatQuery(query, modelId = null) {
  try {
    const payload = { query }
    if (modelId) {
      payload.model_id = modelId
    }

    // Get session token for authentication
    const token = localStorage.getItem('session_token')
    const headers = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await axios.post(
      CHAT_API_URL,
      payload,
      {
        timeout: TIMEOUT,
        headers
      }
    )
    return response.data
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      throw new ChatApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new ChatApiError('Network error. Check your connection.', 0)
    }
    if (error.response.status >= 500) {
      throw new ChatApiError('Service error. Try rephrasing your question.', 500)
    }
    throw new ChatApiError(
      error.response.data?.detail || 'Unknown error',
      error.response.status
    )
  }
}

export async function sendComparisonQuery(query) {
  try {
    // Get session token for authentication
    const token = localStorage.getItem('session_token')
    const headers = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await axios.post(
      '/api/chat/compare',
      { query },
      {
        timeout: 60000, // 60 second timeout for parallel generation
        headers
      }
    )
    return response.data
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      throw new ChatApiError('Request timeout. Please try again.', 408)
    }
    if (!error.response) {
      throw new ChatApiError('Network error. Check your connection.', 0)
    }
    if (error.response.status >= 500) {
      throw new ChatApiError('Service error. Try rephrasing your question.', 500)
    }
    throw new ChatApiError(
      error.response.data?.detail || 'Unknown error',
      error.response.status
    )
  }
}

export async function recordModelSelection(selectionData) {
  try {
    // Get session token for authentication
    const token = localStorage.getItem('session_token')
    const headers = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await axios.post(
      '/api/chat/comparison/select',
      selectionData,
      {
        timeout: 5000,
        headers
      }
    )
    return response.data
  } catch (error) {
    // Don't throw errors for analytics recording - just log it
    console.error('Failed to record model selection:', error)
    return { status: 'error' }
  }
}
