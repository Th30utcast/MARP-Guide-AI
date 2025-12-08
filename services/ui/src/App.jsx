import { useState } from 'react'
import ChatContainer from './components/ChatContainer'
import Analytics from './components/Analytics'
import Sidebar from './components/Sidebar'
import { resetAnalytics } from './api/analyticsApi'

function App() {
  const [currentPage, setCurrentPage] = useState('chat')

  const handleReset = async () => {
    if (confirm('Are you sure you want to reset everything? This will clear all chat messages, model selection, and analytics data.')) {
      try {
        // Clear backend analytics data
        await resetAnalytics()

        // Clear localStorage
        localStorage.removeItem('selectedModel')
        localStorage.removeItem('comparisonShown')

        // Reload the page to reset state
        window.location.reload()
      } catch (error) {
        console.error('Error during reset:', error)
        // Still reload even if analytics reset fails
        localStorage.removeItem('selectedModel')
        localStorage.removeItem('comparisonShown')
        window.location.reload()
      }
    }
  }

  return (
    <div className="h-screen flex" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
      {/* Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onReset={handleReset}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div
          className="flex-1 overflow-hidden"
          style={{ backgroundColor: 'var(--lancaster-bg)' }}
        >
          {currentPage === 'chat' ? <ChatContainer /> : <Analytics />}
        </div>
      </div>
    </div>
  )
}

export default App
