import { useEffect, useRef } from 'react'
import Message from './Message'

function LoadingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div
        className="rounded-xl px-5 py-4 flex items-center gap-3 border"
        style={{
          backgroundColor: 'var(--lancaster-bg)',
          borderColor: 'var(--lancaster-border)',
          boxShadow: 'var(--lancaster-shadow-sm)'
        }}
      >
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'var(--lancaster-red)' }}
        >
          <div className="flex gap-1">
            <div
              className="w-1.5 h-1.5 rounded-full animate-bounce"
              style={{
                backgroundColor: 'var(--lancaster-white)',
                animationDelay: '0s',
                animationDuration: '0.6s'
              }}
            ></div>
            <div
              className="w-1.5 h-1.5 rounded-full animate-bounce"
              style={{
                backgroundColor: 'var(--lancaster-white)',
                animationDelay: '0.1s',
                animationDuration: '0.6s'
              }}
            ></div>
            <div
              className="w-1.5 h-1.5 rounded-full animate-bounce"
              style={{
                backgroundColor: 'var(--lancaster-white)',
                animationDelay: '0.2s',
                animationDuration: '0.6s'
              }}
            ></div>
          </div>
        </div>
        <div>
          <p
            className="text-sm font-medium"
            style={{ color: 'var(--lancaster-text-primary)' }}
          >
            MARP Guide is thinking...
          </p>
          <p
            className="text-xs"
            style={{ color: 'var(--lancaster-text-tertiary)' }}
          >
            Analyzing regulations and formulating response
          </p>
        </div>
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
    <div
      className="flex-1 overflow-y-auto p-6 space-y-4"
      style={{ backgroundColor: 'var(--lancaster-bg)' }}
    >
      {messages.length === 0 && !isLoading && (
        <div className="text-center mt-20 animate-fade-in">
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              boxShadow: 'var(--lancaster-shadow-lg)'
            }}
          >
            <svg
              className="w-10 h-10"
              fill="none"
              stroke="var(--lancaster-white)"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <h2
            className="text-2xl font-bold mb-2"
            style={{ color: 'var(--lancaster-text-primary)' }}
          >
            Welcome to MARP Guide AI
          </h2>
          <p
            className="text-base mb-6 max-w-md mx-auto"
            style={{ color: 'var(--lancaster-text-secondary)' }}
          >
            Ask me anything about Lancaster University's academic regulations and procedures
          </p>
          <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
            {[
              'What are the exam regulations?',
              'How do I submit extenuating circumstances?',
              'What is the grading system?'
            ].map((example, idx) => (
              <button
                key={idx}
                className="px-4 py-2 rounded-lg text-sm border"
                style={{
                  backgroundColor: 'var(--lancaster-white)',
                  borderColor: 'var(--lancaster-border)',
                  color: 'var(--lancaster-text-secondary)',
                  boxShadow: 'var(--lancaster-shadow-sm)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = 'var(--lancaster-red)'
                  e.target.style.color = 'var(--lancaster-red)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = 'var(--lancaster-border)'
                  e.target.style.color = 'var(--lancaster-text-secondary)'
                }}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {messages.map((msg, idx) => (
        <Message key={idx} message={msg} />
      ))}

      {isLoading && <LoadingIndicator />}

      {error && (
        <div
          className="rounded-xl p-5 border-2 animate-fade-in"
          style={{
            backgroundColor: '#FEF2F2',
            borderColor: '#FCA5A5'
          }}
        >
          <div className="flex items-start gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: '#EF4444' }}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="white"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <p
                className="font-semibold mb-1"
                style={{ color: '#991B1B' }}
              >
                Something went wrong
              </p>
              <p className="text-sm mb-3" style={{ color: '#DC2626' }}>
                {error}
              </p>
              <button
                onClick={() => {
                  onClearError()
                  onRetry()
                }}
                className="text-sm font-semibold px-4 py-2 rounded-lg"
                style={{
                  backgroundColor: '#EF4444',
                  color: 'white'
                }}
                onMouseEnter={(e) =>
                  (e.target.style.backgroundColor = '#DC2626')
                }
                onMouseLeave={(e) =>
                  (e.target.style.backgroundColor = '#EF4444')
                }
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      <div ref={endRef} />
    </div>
  )
}

export default MessageList
