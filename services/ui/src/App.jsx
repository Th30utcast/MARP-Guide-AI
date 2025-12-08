import ChatContainer from './components/ChatContainer'
import lancasterLogo from '/LancasterLogo.png'

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
      <header
        className="border-b px-6 py-4 backdrop-blur-sm"
        style={{
          backgroundColor: 'var(--lancaster-white)',
          borderColor: 'var(--lancaster-border)',
          boxShadow: 'var(--lancaster-shadow-sm)'
        }}
      >
        <div className="container mx-auto max-w-5xl flex items-center gap-4">
          {/* Lancaster Logo */}
          <img
            src={lancasterLogo}
            alt="Lancaster University"
            className="h-12 w-auto object-contain"
            style={{ filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))' }}
          />

          {/* Divider */}
          <div
            className="h-10 w-px"
            style={{ backgroundColor: 'var(--lancaster-border)' }}
          />

          {/* Title Section */}
          <div className="flex-1">
            <h1
              className="text-2xl font-bold tracking-tight"
              style={{ color: 'var(--lancaster-red)' }}
            >
              MARP Guide AI
            </h1>
            <p
              className="text-sm"
              style={{ color: 'var(--lancaster-text-secondary)' }}
            >
              Your intelligent assistant for Lancaster's Manual of Academic Regulations and Procedures
            </p>
          </div>

          {/* Beta Badge */}
          <div
            className="px-3 py-1 rounded-full text-xs font-semibold"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              color: 'var(--lancaster-white)'
            }}
          >
            BETA
          </div>
        </div>
      </header>

      <main className="container mx-auto max-w-5xl h-[calc(100vh-96px)] py-6 px-6">
        <div
          className="h-full rounded-xl overflow-hidden"
          style={{
            backgroundColor: 'var(--lancaster-white)',
            boxShadow: 'var(--lancaster-shadow-md)'
          }}
        >
          <ChatContainer />
        </div>
      </main>
    </div>
  )
}

export default App
