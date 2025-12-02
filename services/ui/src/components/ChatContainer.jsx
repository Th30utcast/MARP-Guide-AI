import { useChat } from '../hooks/useChat'
import MessageList from './MessageList'
import ChatInput from './ChatInput'

function ChatContainer() {
  const { messages, isLoading, error, sendMessage, retryLastQuery, clearError } = useChat()

  return (
    <div className="flex flex-col h-full">
      <MessageList
        messages={messages}
        isLoading={isLoading}
        error={error}
        onRetry={retryLastQuery}
        onClearError={clearError}
      />
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}

export default ChatContainer
