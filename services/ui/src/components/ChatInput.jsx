import { useState } from 'react'

function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t p-6"
      style={{
        backgroundColor: 'var(--lancaster-white)',
        borderColor: 'var(--lancaster-border)'
      }}
    >
      <div className="flex gap-3 items-end">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask a question about MARP regulations..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-xl px-5 py-4 focus:outline-none border-2"
            style={{
              backgroundColor: 'var(--lancaster-bg)',
              borderColor: isFocused ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
              color: 'var(--lancaster-text-primary)',
              boxShadow: isFocused ? 'var(--lancaster-shadow-md)' : 'var(--lancaster-shadow-sm)',
              minHeight: '56px',
              maxHeight: '200px'
            }}
          />

          {/* Character counter for long messages */}
          {input.length > 100 && (
            <span
              className="absolute bottom-2 right-3 text-xs"
              style={{ color: 'var(--lancaster-text-tertiary)' }}
            >
              {input.length}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="rounded-xl font-semibold disabled:cursor-not-allowed flex items-center gap-2 px-6 py-4 shadow-sm hover:shadow-md"
          style={{
            backgroundColor: disabled || !input.trim() ? 'var(--lancaster-border)' : 'var(--lancaster-red)',
            color: disabled || !input.trim() ? 'var(--lancaster-text-tertiary)' : 'var(--lancaster-white)',
            minHeight: '56px',
            transform: disabled || !input.trim() ? 'scale(1)' : 'scale(1)',
          }}
          onMouseEnter={(e) => {
            if (!disabled && input.trim()) {
              e.target.style.backgroundColor = 'var(--lancaster-red-dark)'
              e.target.style.transform = 'scale(1.02)'
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled && input.trim()) {
              e.target.style.backgroundColor = 'var(--lancaster-red)'
              e.target.style.transform = 'scale(1)'
            }
          }}
        >
          <span>Send</span>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Helpful hint */}
      <p
        className="text-xs mt-2 flex items-center gap-2"
        style={{ color: 'var(--lancaster-text-tertiary)' }}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  )
}

export default ChatInput
