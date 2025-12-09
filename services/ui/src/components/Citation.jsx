import { useState } from 'react'

function Citation({ citation }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <a
      href={citation.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg p-3 text-sm border group"
      style={{
        backgroundColor: isHovered ? 'var(--lancaster-white)' : 'transparent',
        borderColor: isHovered ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
        boxShadow: isHovered ? 'var(--lancaster-shadow-sm)' : 'none',
        transform: isHovered ? 'translateX(4px)' : 'translateX(0)'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center gap-3">
        {/* Document icon */}
        <div
          className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{
            backgroundColor: isHovered ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
            color: isHovered ? 'var(--lancaster-white)' : 'var(--lancaster-text-tertiary)'
          }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p
            className="font-medium truncate"
            style={{
              color: isHovered ? 'var(--lancaster-red)' : 'var(--lancaster-text-primary)'
            }}
          >
            {citation.title}
          </p>
          <p
            className="text-xs flex items-center gap-1"
            style={{ color: 'var(--lancaster-text-tertiary)' }}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Page {citation.page}
          </p>
        </div>

        {/* External link icon */}
        <div
          className="flex-shrink-0"
          style={{
            color: isHovered ? 'var(--lancaster-red)' : 'var(--lancaster-text-tertiary)'
          }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </div>
      </div>
    </a>
  )
}

export default Citation
