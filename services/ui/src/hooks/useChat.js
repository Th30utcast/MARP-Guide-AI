import { useState } from 'react'
import { sendChatQuery, sendComparisonQuery } from '../api/chatApi'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastQuery, setLastQuery] = useState('')
  const [comparisonData, setComparisonData] = useState(null)
  const [selectedModel, setSelectedModel] = useState(() => {
    // Load from localStorage if exists
    return localStorage.getItem('selectedModel') || null
  })
  const [queryCount, setQueryCount] = useState(0)

  const sendMessage = async (query) => {
    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)
    setLastQuery(query)

    try {
      // Count how many user queries have been sent
      const currentQueryCount = queryCount + 1
      setQueryCount(currentQueryCount)

      // First query: Use GPT-4o Mini by default (no comparison)
      // Second query: Trigger comparison if no model selected yet
      // Third+ query: Use selected model
      if (currentQueryCount === 2 && !selectedModel) {
        // Second query - trigger comparison
        const comparisonResult = await sendComparisonQuery(query)
        setComparisonData(comparisonResult)
        setIsLoading(false)
        // Don't add assistant message yet - wait for user to select model
        return
      }

      // Normal flow: use GPT-4o Mini (first query) or selected model (after selection)
      const response = await sendChatQuery(query)
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations || []
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleModelSelection = (modelId) => {
    // Save selection to state and localStorage
    setSelectedModel(modelId)
    localStorage.setItem('selectedModel', modelId)

    // Find the selected model's answer from comparison data
    const selectedResult = comparisonData.results.find(r => r.model_id === modelId)

    if (selectedResult) {
      // Add the selected model's answer as assistant message
      const assistantMessage = {
        role: 'assistant',
        content: selectedResult.answer,
        citations: selectedResult.citations || [],
        modelName: selectedResult.model_name
      }
      setMessages(prev => [...prev, assistantMessage])
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
    setSelectedModel(null)
    localStorage.removeItem('selectedModel')
    setMessages([])
    setQueryCount(0)
  }

  return {
    messages,
    isLoading,
    error,
    comparisonData,
    selectedModel,
    sendMessage,
    handleModelSelection,
    retryLastQuery,
    clearError,
    resetModelSelection
  }
}
