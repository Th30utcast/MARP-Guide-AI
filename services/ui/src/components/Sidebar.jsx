import { useState } from 'react'

function Sidebar({ currentPage, onPageChange, onReset, onLogout, user }) {
  const [isHovered, setIsHovered] = useState(null)

  const menuItems = [
    {
      id: 'chat',
      name: 'Chat',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )
    },
    {
      id: 'analytics',
      name: 'Analytics',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      )
    }
  ]

  return (
    <div
      className="h-screen flex flex-col border-r"
      style={{
        width: '240px',
        backgroundColor: 'var(--lancaster-white)',
        borderColor: 'var(--lancaster-border)'
      }}
    >
      {/* Logo/Header */}
      <div className="p-6 border-b" style={{ borderColor: 'var(--lancaster-border)' }}>
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold"
            style={{ backgroundColor: 'var(--lancaster-red)' }}
          >
            AI
          </div>
          <div>
            <h1 className="font-bold text-lg" style={{ color: 'var(--lancaster-text-primary)' }}>
              MARP Guide
            </h1>
            <p className="text-xs" style={{ color: 'var(--lancaster-text-tertiary)' }}>
              Lancaster University
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            onMouseEnter={() => setIsHovered(item.id)}
            onMouseLeave={() => setIsHovered(null)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left"
            style={{
              backgroundColor:
                currentPage === item.id
                  ? 'var(--lancaster-red)'
                  : isHovered === item.id
                  ? 'var(--lancaster-bg)'
                  : 'transparent',
              color:
                currentPage === item.id
                  ? 'var(--lancaster-white)'
                  : 'var(--lancaster-text-primary)'
            }}
          >
            {item.icon}
            <span className="font-medium">{item.name}</span>
          </button>
        ))}
      </nav>

      {/* Reset Button */}
      <div className="p-4 border-t space-y-2" style={{ borderColor: 'var(--lancaster-border)' }}>
        <button
          onClick={onReset}
          onMouseEnter={() => setIsHovered('reset')}
          onMouseLeave={() => setIsHovered(null)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left"
          style={{
            backgroundColor: isHovered === 'reset' ? 'var(--lancaster-bg)' : 'transparent',
            color: 'var(--lancaster-text-secondary)'
          }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span className="font-medium">Reset Chat</span>
        </button>

        {/* User Info & Logout */}
        {user && (
          <div className="pt-2">
            <div className="px-4 py-2">
              <p className="text-xs font-semibold truncate" style={{ color: 'var(--lancaster-text-primary)' }}>
                {user.email}
              </p>
            </div>
            <button
              onClick={onLogout}
              onMouseEnter={() => setIsHovered('logout')}
              onMouseLeave={() => setIsHovered(null)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left"
              style={{
                backgroundColor: isHovered === 'logout' ? 'var(--lancaster-bg)' : 'transparent',
                color: 'var(--lancaster-red)'
              }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="font-medium">Logout</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar
