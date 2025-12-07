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
        <div className="p-2 text-center text-xs text-gray-400 border-b" style={{ borderColor: '#3f4147', backgroundColor: '#2b2d31' }}>
          Using: {selectedModel.split('/')[1].split(':')[0]}
          <button
            onClick={resetModelSelection}
            className="ml-3 text-blue-400 hover:underline"
          >
            Change Model
          </button>
        </div>
      )}

      {comparisonData ? (
        <div className="flex-1 overflow-y-auto p-4">
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
