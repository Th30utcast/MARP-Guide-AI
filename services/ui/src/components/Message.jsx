import ReactMarkdown from 'react-markdown'
import Citation from './Citation'

function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex ${isUser ? 'justify-end animate-slide-in-right' : 'justify-start animate-slide-in-left'}`}
    >
      <div
        className={`max-w-[75%] rounded-xl px-5 py-4 ${
          isUser ? '' : 'border'
        }`}
        style={
          isUser
            ? {
                backgroundColor: 'var(--lancaster-red)',
                color: 'var(--lancaster-white)',
                boxShadow: 'var(--lancaster-shadow-sm)'
              }
            : {
                backgroundColor: 'var(--lancaster-bg)',
                borderColor: 'var(--lancaster-border)',
                color: 'var(--lancaster-text-primary)',
                boxShadow: 'var(--lancaster-shadow-sm)'
              }
        }
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
              style={{
                backgroundColor: 'var(--lancaster-red)',
                boxShadow: 'var(--lancaster-shadow-sm)'
              }}
            >
              AI
            </div>
            <div>
              <span
                className="text-sm font-semibold"
                style={{ color: 'var(--lancaster-text-primary)' }}
              >
                MARP Guide
              </span>
              <p
                className="text-xs"
                style={{ color: 'var(--lancaster-text-tertiary)' }}
              >
                Lancaster University
              </p>
            </div>
          </div>
        )}

        <div
          className={`prose prose-sm max-w-none ${
            isUser ? 'prose-invert' : ''
          }`}
          style={
            isUser
              ? { color: 'var(--lancaster-white)' }
              : { color: 'var(--lancaster-text-primary)' }
          }
        >
          <ReactMarkdown
            components={{
              p: ({ children }) => {
                // Convert children to string and style citation numbers
                const text = String(children)
                // Replace [1], [2], etc. with italic styled versions
                const styledText = text.replace(/\[(\d+)\]/g, (match) => {
                  return `<i style="font-weight: 600; opacity: 0.9;">${match}</i>`
                })

                // If citations were found, render with HTML
                if (styledText !== text) {
                  return <p dangerouslySetInnerHTML={{ __html: styledText }} />
                }

                return <p>{children}</p>
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 space-y-2 border-t" style={{ borderColor: isUser ? 'rgba(255,255,255,0.2)' : 'var(--lancaster-border)' }}>
            <p
              className="text-xs font-semibold flex items-center gap-2"
              style={{ color: isUser ? 'rgba(255,255,255,0.9)' : 'var(--lancaster-text-secondary)' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Sources
            </p>
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
