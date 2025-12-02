import { useState } from 'react'
import { sendChatQuery } from '../api/chatApi'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastQuery, setLastQuery] = useState('')

  const sendMessage = async (query) => {
    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)
    setLastQuery(query)

    try {
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

  const retryLastQuery = () => {
    if (lastQuery) {
      sendMessage(lastQuery)
    }
  }

  const clearError = () => {
    setError(null)
  }

  return { messages, isLoading, error, sendMessage, retryLastQuery, clearError }
}
