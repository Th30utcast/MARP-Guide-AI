import axios from 'axios'

// Chat API endpoint - can be configured via environment variable
const CHAT_API_URL = import.meta.env.VITE_CHAT_API_URL || '/api/chat'
const TIMEOUT = 30000 // 30 second timeout for normal queries

/**
 * Custom error class for chat API errors.
 * Includes HTTP status code for better error handling.
 */
class ChatApiError extends Error {
  constructor(message, statusCode) {
    super(message)
    this.statusCode = statusCode
    this.name = 'ChatApiError'
  }
}

/**
 * Sends a chat query to the backend API and retrieves a RAG-enhanced response.
 * The response includes an AI-generated answer and citations from retrieved documents.
 *
 * @param {string} query - The user's question or prompt
 * @param {string|null} modelId - Optional AI model ID (e.g., "openai/gpt-4o"). Uses default if null.
 * @returns {Promise<Object>} Response containing answer and citations
 * @throws {ChatApiError} If request fails or times out
 */
export async function sendChatQuery(query, modelId = null) {
  try {
    const payload = { query }
    if (modelId) {
      payload.model_id = modelId // Specify which AI model to use
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
    // Handle different error types with user-friendly messages
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

/**
 * Sends a comparison query that generates responses from multiple AI models in parallel.
 * Used on the user's second query to let them compare and choose their preferred model.
 * Returns responses from multiple models for side-by-side comparison.
 *
 * @param {string} query - The user's question to send to multiple models
 * @returns {Promise<Object>} Object containing results array with responses from each model
 * @throws {ChatApiError} If request fails or times out
 */
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
        timeout: 60000, // 60 second timeout - longer because parallel generation takes time
        headers
      }
    )
    return response.data
  } catch (error) {
    // Handle different error types with user-friendly messages
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

/**
 * Records the user's model selection after comparison for analytics purposes.
 * Tracks which model was chosen, query details, and performance metrics.
 * Used to analyze user preferences and model performance over time.
 *
 * @param {Object} selectionData - Data about the model selection
 * @param {string} selectionData.query - The query that was used for comparison
 * @param {string} selectionData.model_id - The chosen model ID
 * @param {string} selectionData.answer - The answer from the selected model
 * @param {number} selectionData.citation_count - Number of citations in the response
 * @param {number} selectionData.retrieval_count - Number of documents retrieved
 * @param {number} selectionData.latency_ms - Response time in milliseconds
 * @returns {Promise<Object>} Confirmation of recorded selection
 */
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
    // Non-critical failure - don't block user experience if analytics recording fails
    console.error('Failed to record model selection:', error)
    return { status: 'error' }
  }
}
