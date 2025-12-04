import { useState } from 'react'

function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState('')

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
    <form onSubmit={handleSubmit} className="border-t p-4" style={{ backgroundColor: '#2b2d31', borderColor: '#3f4147' }}>
      <div className="flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about MARP..."
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none rounded-lg px-4 py-3 focus:outline-none text-gray-100 placeholder-gray-500"
          style={{
            backgroundColor: '#383a40',
            border: 'none'
          }}
          onFocus={(e) => e.target.style.outline = '2px solid #3ba55d'}
          onBlur={(e) => e.target.style.outline = 'none'}
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-3 text-white rounded-lg transition-colors font-medium disabled:cursor-not-allowed"
          style={{
            backgroundColor: disabled || !input.trim() ? '#2b2d31' : '#3ba55d',
            color: disabled || !input.trim() ? '#6b7280' : 'white'
          }}
          onMouseEnter={(e) => {
            if (!disabled && input.trim()) e.target.style.backgroundColor = '#2d7d46'
          }}
          onMouseLeave={(e) => {
            if (!disabled && input.trim()) e.target.style.backgroundColor = '#3ba55d'
          }}
        >
          Send
        </button>
      </div>
    </form>
  )
}

export default ChatInput
