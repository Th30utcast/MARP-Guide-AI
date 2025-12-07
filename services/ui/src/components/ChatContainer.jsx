import { useChat } from '../hooks/useChat'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import ModelComparison from './ModelComparison'

function ChatContainer() {
  const {
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
  } = useChat()

  return (
    <div className="flex flex-col h-full">
      {selectedModel && (
        <div
          className="px-6 py-3 border-b flex items-center justify-center gap-2 text-sm"
          style={{
            backgroundColor: 'var(--lancaster-bg)',
            borderColor: 'var(--lancaster-border)'
          }}
        >
          <div
            className="flex items-center gap-2 px-4 py-2 rounded-lg"
            style={{
              backgroundColor: 'var(--lancaster-white)',
              border: '1px solid var(--lancaster-border)'
            }}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="var(--lancaster-red)"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span style={{ color: 'var(--lancaster-text-secondary)' }}>
              Using: <span style={{ color: 'var(--lancaster-red)', fontWeight: 600 }}>
                {selectedModel.split('/')[1].split(':')[0]}
              </span>
            </span>
          </div>
          <button
            onClick={resetModelSelection}
            className="px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
            style={{
              backgroundColor: 'var(--lancaster-white)',
              color: 'var(--lancaster-red)',
              border: '1px solid var(--lancaster-red)'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--lancaster-red)'
              e.target.style.color = 'var(--lancaster-white)'
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'var(--lancaster-white)'
              e.target.style.color = 'var(--lancaster-red)'
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Change Model
          </button>
        </div>
      )}

      {comparisonData ? (
        <div className="flex-1 overflow-y-auto">
          <ModelComparison
            comparisonData={comparisonData}
            onModelSelect={handleModelSelection}
          />
        </div>
      ) : (
        <MessageList
          messages={messages}
          isLoading={isLoading}
          error={error}
          onRetry={retryLastQuery}
          onClearError={clearError}
        />
      )}

      <ChatInput onSend={sendMessage} disabled={isLoading || !!comparisonData} />
    </div>
  )
}

export default ChatContainer
