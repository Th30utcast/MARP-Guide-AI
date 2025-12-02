import { useEffect, useRef } from 'react'
import Message from './Message'

function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="border-l-4 rounded-lg px-4 py-3 flex items-center gap-2" style={{ backgroundColor: '#383a40', borderLeftColor: '#3ba55d' }}>
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#3ba55d', animationDelay: '0s' }}></div>
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#3ba55d', animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#3ba55d', animationDelay: '0.4s' }}></div>
        </div>
        <span className="text-sm text-gray-300">MARP Guide is thinking...</span>
      </div>
    </div>
  )
}

function MessageList({ messages, isLoading, error, onRetry, onClearError }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-20">
          <p className="text-lg">Ask a question about MARP...</p>
        </div>
      )}

      {messages.map((msg, idx) => (
        <Message key={idx} message={msg} />
      ))}

      {isLoading && <LoadingIndicator />}

      {error && (
        <div className="rounded-lg p-4" style={{ backgroundColor: '#3c2a2a', borderLeft: '4px solid #ed4245' }}>
          <p className="text-red-200 mb-2">{error}</p>
          <button
            onClick={() => { onClearError(); onRetry(); }}
            className="text-sm text-white px-3 py-1 rounded transition-colors"
            style={{ backgroundColor: '#ed4245' }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#c03537'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#ed4245'}
          >
            Try Again
          </button>
        </div>
      )}

      <div ref={endRef} />
    </div>
  )
}

export default MessageList
