import ReactMarkdown from 'react-markdown'
import Citation from './Citation'

function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 ${isUser ? 'text-white' : 'text-gray-100'}`}
        style={isUser ? { backgroundColor: '#5865f2' } : { backgroundColor: '#383a40', borderLeft: '4px solid #3ba55d' }}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className="w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: '#3ba55d' }}>
              AI
            </div>
            <span className="text-xs text-gray-400">MARP Guide</span>
          </div>
        )}
        <div className="prose prose-sm max-w-none prose-invert">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.citations && message.citations.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold text-gray-400">Sources:</p>
            {message.citations.map((citation, idx) => (
              <Citation key={idx} citation={citation} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Message
