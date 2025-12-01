import ChatContainer from './components/ChatContainer'

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#2b2d31' }}>
      <header className="border-b px-4 py-3" style={{ backgroundColor: '#1e1f22', borderColor: '#3f4147' }}>
        <h1 className="text-xl font-semibold text-gray-100">
          MARP Guide AI
        </h1>
        <p className="text-sm text-gray-400">Ask questions about Lancaster's MARP</p>
      </header>
      <main className="container mx-auto max-w-4xl h-[calc(100vh-80px)]">
        <ChatContainer />
      </main>
    </div>
  )
}

export default App
