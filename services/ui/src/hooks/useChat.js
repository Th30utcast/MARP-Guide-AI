import { useState } from 'react'
import { sendChatQuery, sendComparisonQuery, recordModelSelection } from '../api/chatApi'

/**
 * Custom React hook that manages the chat interface state and interactions.
 * Handles message history, model selection, query processing, and the comparison workflow.
 *
 * This hook implements a three-stage user experience:
 * 1. First query: Uses default GPT-4o Mini model
 * 2. Second query: Triggers model comparison (showing multiple model responses)
 * 3. Subsequent queries: Uses the user's selected model from comparison
 *
 * @returns {Object} Chat state and methods for interacting with the chat system
 */
export function useChat() {
  // Chat message history - persisted to localStorage for session continuity
  const [messages, setMessages] = useState(() => {
    // Load messages from localStorage on initial render
    const saved = localStorage.getItem('chatMessages')
    return saved ? JSON.parse(saved) : []
  })

  // Loading state - true while waiting for API response
  const [isLoading, setIsLoading] = useState(false)

  // Error message from failed API calls
  const [error, setError] = useState(null)

  // Stores the most recent query for retry functionality
  const [lastQuery, setLastQuery] = useState('')

  // Model comparison results (shown on second query only)
  const [comparisonData, setComparisonData] = useState(null)

  // Currently selected AI model ID (e.g., "openai/gpt-4o-mini")
  const [selectedModel, setSelectedModel] = useState(() => {
    return localStorage.getItem('selectedModel') || null
  })

  // Tracks number of queries submitted (used to trigger comparison on query #2)
  const [queryCount, setQueryCount] = useState(() => {
    const saved = localStorage.getItem('queryCount')
    return saved ? parseInt(saved) : 0
  })

  // Controls visibility of manual model selector dropdown
  const [showModelSelector, setShowModelSelector] = useState(false)

  // Flag indicating if user has seen and completed the comparison workflow
  const [comparisonShown, setComparisonShown] = useState(() => {
    return localStorage.getItem('comparisonShown') === 'true'
  })

  /**
   * Sends a user query to the chat API and handles the response.
   * Implements the tiered model selection experience:
   * - Query 1: Uses default model (GPT-4o Mini)
   * - Query 2: Triggers comparison between multiple models for user to choose
   * - Query 3+: Uses the user's selected model
   *
   * @param {string} query - The user's question or prompt
   */
  const sendMessage = async (query) => {
    // Close model selector dropdown if open
    setShowModelSelector(false)

    // Add user message to chat history immediately for responsive UI
    const userMessage = { role: 'user', content: query }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    localStorage.setItem('chatMessages', JSON.stringify(newMessages))

    setIsLoading(true)
    setError(null)
    setLastQuery(query)

    try {
      // Increment query counter to track when to trigger comparison
      const currentQueryCount = queryCount + 1
      setQueryCount(currentQueryCount)
      localStorage.setItem('queryCount', currentQueryCount.toString())

      // On second query, show model comparison (unless already shown)
      // This lets user experience default model first, then choose their preferred model
      if (currentQueryCount === 2 && !comparisonShown) {
        const comparisonResult = await sendComparisonQuery(query)
        setComparisonData(comparisonResult)
        setIsLoading(false)
        return
      }

      // Normal query flow: use default model on first query, selected model afterwards
      const response = await sendChatQuery(query, selectedModel)
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations || [] // Citations from retrieved documents
      }
      const updatedMessages = [...newMessages, assistantMessage]
      setMessages(updatedMessages)
      localStorage.setItem('chatMessages', JSON.stringify(updatedMessages))
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Handles user selecting a model from the comparison view.
   * Records the selection for analytics, adds the chosen response to chat, and closes comparison.
   *
   * @param {string} modelId - The ID of the selected model (e.g., "openai/gpt-4o")
   */
  const handleModelSelection = async (modelId) => {
    // Save selected model for future queries
    setSelectedModel(modelId)
    localStorage.setItem('selectedModel', modelId)

    // Mark that user has completed the comparison workflow
    setComparisonShown(true)
    localStorage.setItem('comparisonShown', 'true')

    // Find the selected model's response from comparison results
    const selectedResult = comparisonData.results.find(r => r.model_id === modelId)

    if (selectedResult) {
      try {
        // Record selection to analytics backend for tracking model preferences
        await recordModelSelection({
          query: comparisonData.query,
          model_id: selectedResult.model_id,
          answer: selectedResult.answer,
          citation_count: selectedResult.citations?.length || 0,
          retrieval_count: comparisonData.retrieval_count,
          latency_ms: comparisonData.latency_ms
        })
      } catch (error) {
        console.error('Failed to record model selection:', error)
      }

      // Add selected model's response to chat history
      const assistantMessage = {
        role: 'assistant',
        content: selectedResult.answer,
        citations: selectedResult.citations || [],
        modelName: selectedResult.model_name
      }
      const updatedMessages = [...messages, assistantMessage]
      setMessages(updatedMessages)
      localStorage.setItem('chatMessages', JSON.stringify(updatedMessages))
    }

    // Close comparison view
    setComparisonData(null)
  }

  /**
   * Retries the most recent query if there was an error.
   * Useful for handling temporary network or server issues.
   */
  const retryLastQuery = () => {
    if (lastQuery) {
      sendMessage(lastQuery)
    }
  }

  /**
   * Clears the current error message from state.
   */
  const clearError = () => {
    setError(null)
  }

  /**
   * Resets model selection and opens the model selector.
   * Allows user to manually choose a different model after initial selection.
   */
  const resetModelSelection = () => {
    setSelectedModel(null)
    localStorage.removeItem('selectedModel')
    setShowModelSelector(true)
  }

  /**
   * Handles direct model selection from the manual model selector dropdown.
   * Used when user wants to change models outside of the comparison workflow.
   *
   * @param {string} modelId - The ID of the model to switch to
   */
  const handleDirectModelSelection = (modelId) => {
    setSelectedModel(modelId)
    localStorage.setItem('selectedModel', modelId)
    setShowModelSelector(false)
  }

  /**
   * Cancels the manual model selection and restores the previous model.
   * Used when user closes the model selector without making a choice.
   */
  const cancelModelSelection = () => {
    const previousModel = localStorage.getItem('selectedModel')
    if (previousModel) {
      setSelectedModel(previousModel)
    }
    setShowModelSelector(false)
  }

  return {
    messages,
    isLoading,
    error,
    comparisonData,
    selectedModel,
    showModelSelector,
    sendMessage,
    handleModelSelection,
    handleDirectModelSelection,
    cancelModelSelection,
    retryLastQuery,
    clearError,
    resetModelSelection
  }
}
