import { useState } from 'react'
import { sendChatQuery, sendComparisonQuery, recordModelSelection } from '../api/chatApi'

export function useChat() {
  const [messages, setMessages] = useState(() => {
    // Load messages from localStorage if exists
    const saved = localStorage.getItem('chatMessages')
    return saved ? JSON.parse(saved) : []
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastQuery, setLastQuery] = useState('')
  const [comparisonData, setComparisonData] = useState(null)
  const [selectedModel, setSelectedModel] = useState(() => {
    // Load from localStorage if exists
    return localStorage.getItem('selectedModel') || null
  })
  const [queryCount, setQueryCount] = useState(() => {
    // Load query count from localStorage
    const saved = localStorage.getItem('queryCount')
    return saved ? parseInt(saved) : 0
  })
  const [showModelSelector, setShowModelSelector] = useState(false)
  const [comparisonShown, setComparisonShown] = useState(() => {
    // Track if comparison was already shown to avoid showing it again
    return localStorage.getItem('comparisonShown') === 'true'
  })

  const sendMessage = async (query) => {
    // Close model selector if it's open
    setShowModelSelector(false)

    const userMessage = { role: 'user', content: query }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    localStorage.setItem('chatMessages', JSON.stringify(newMessages))

    setIsLoading(true)
    setError(null)
    setLastQuery(query)

    try {
      // Count how many user queries have been sent
      const currentQueryCount = queryCount + 1
      setQueryCount(currentQueryCount)
      localStorage.setItem('queryCount', currentQueryCount.toString())

      // First query: Use GPT-4o Mini by default (no comparison)
      // Second query: Trigger comparison if comparison hasn't been shown yet
      // Third+ query: Use selected model
      if (currentQueryCount === 2 && !comparisonShown) {
        // Second query - trigger comparison
        const comparisonResult = await sendComparisonQuery(query)
        setComparisonData(comparisonResult)
        // Don't mark as shown yet - only when they select a model
        setIsLoading(false)
        // Don't add assistant message yet - wait for user to select model
        return
      }

      // Normal flow: use GPT-4o Mini (first query) or selected model (after selection)
      const response = await sendChatQuery(query, selectedModel)
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations || []
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

  const handleModelSelection = async (modelId) => {
    // Save selection to state and localStorage
    setSelectedModel(modelId)
    localStorage.setItem('selectedModel', modelId)

    // Mark comparison as shown only after user selects a model
    setComparisonShown(true)
    localStorage.setItem('comparisonShown', 'true')

    // Find the selected model's answer from comparison data
    const selectedResult = comparisonData.results.find(r => r.model_id === modelId)

    if (selectedResult) {
      // Record the model selection in analytics
      try {
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
        // Continue anyway - analytics failure shouldn't block the user
      }

      // Add the selected model's answer as assistant message
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

    // Clear comparison data
    setComparisonData(null)
  }

  const retryLastQuery = () => {
    if (lastQuery) {
      sendMessage(lastQuery)
    }
  }

  const clearError = () => {
    setError(null)
  }

  const resetModelSelection = () => {
    // Clear current model selection and show selector
    setSelectedModel(null)
    localStorage.removeItem('selectedModel')
    setShowModelSelector(true)
  }

  const handleDirectModelSelection = (modelId) => {
    // Handle model selection from the manual selector UI
    setSelectedModel(modelId)
    localStorage.setItem('selectedModel', modelId)
    setShowModelSelector(false)
    // Keep current query count so comparison can still trigger on 2nd query if needed
  }

  const cancelModelSelection = () => {
    // User cancelled - restore previous selection if exists
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
