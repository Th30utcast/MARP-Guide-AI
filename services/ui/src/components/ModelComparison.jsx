import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Citation from './Citation'

function ModelComparisonCard({ result, isSelected, onSelect }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="cursor-pointer rounded-xl p-5 border-2 transition-all animate-fade-in"
      style={{
        backgroundColor: isSelected ? 'var(--lancaster-white)' : 'var(--lancaster-bg)',
        borderColor: isSelected ? 'var(--lancaster-red)' : isHovered ? 'var(--lancaster-border-hover)' : 'var(--lancaster-border)',
        boxShadow: isSelected ? 'var(--lancaster-shadow-md)' : isHovered ? 'var(--lancaster-shadow-sm)' : 'none',
        transform: isSelected ? 'scale(1.02)' : isHovered ? 'scale(1.01)' : 'scale(1)'
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center font-bold"
            style={{
              backgroundColor: isSelected ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
              color: isSelected ? 'var(--lancaster-white)' : 'var(--lancaster-text-tertiary)'
            }}
          >
            AI
          </div>
          <div>
            <h3
              className="font-semibold text-base"
              style={{ color: 'var(--lancaster-text-primary)' }}
            >
              {result.model_name}
            </h3>
            <p
              className="text-xs"
              style={{ color: 'var(--lancaster-text-tertiary)' }}
            >
              {result.model_id}
            </p>
          </div>
        </div>

        {isSelected && (
          <div
            className="px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              color: 'var(--lancaster-white)'
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Selected
          </div>
        )}
      </div>

      <div
        className="prose prose-sm max-w-none mb-4"
        style={{ color: 'var(--lancaster-text-primary)' }}
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
          {result.answer}
        </ReactMarkdown>
      </div>

      {result.citations && result.citations.length > 0 && (
        <div className="mt-4 pt-4 space-y-2 border-t" style={{ borderColor: 'var(--lancaster-border)' }}>
          <p
            className="text-xs font-semibold flex items-center gap-2"
            style={{ color: 'var(--lancaster-text-secondary)' }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Sources
          </p>
          {result.citations.map((citation, idx) => (
            <Citation key={idx} citation={citation} />
          ))}
        </div>
      )}
    </div>
  )
}

function ModelComparison({ comparisonData, onModelSelect }) {
  const [selectedModel, setSelectedModel] = useState(null)

  const handleSelect = (modelId) => {
    setSelectedModel(modelId)
  }

  const handleConfirm = () => {
    if (selectedModel) {
      onModelSelect(selectedModel)
    }
  }

  return (
    <div className="space-y-6 p-6" style={{ backgroundColor: 'var(--lancaster-bg)' }}>
      {/* Header Section */}
      <div
        className="rounded-xl p-6 border-l-4 animate-fade-in"
        style={{
          backgroundColor: 'var(--lancaster-white)',
          borderLeftColor: 'var(--lancaster-red)',
          boxShadow: 'var(--lancaster-shadow-md)'
        }}
      >
        <div className="flex items-start gap-4">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: 'var(--lancaster-red)' }}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="var(--lancaster-white)"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h2
              className="text-xl font-bold mb-2"
              style={{ color: 'var(--lancaster-red)' }}
            >
              Compare AI Models
            </h2>
            <p
              className="text-sm mb-2"
              style={{ color: 'var(--lancaster-text-primary)' }}
            >
              Your query: <span className="font-semibold italic">"{comparisonData.query}"</span>
            </p>
            <p
              className="text-xs"
              style={{ color: 'var(--lancaster-text-secondary)' }}
            >
              Review responses from 3 different AI models and select your preferred one
            </p>
          </div>
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 gap-4">
        {comparisonData.results.map((result, idx) => (
          <ModelComparisonCard
            key={result.model_id}
            result={result}
            isSelected={selectedModel === result.model_id}
            onSelect={() => handleSelect(result.model_id)}
          />
        ))}
      </div>

      {/* Confirm Button */}
      <div className="flex justify-center pt-2">
        <button
          onClick={handleConfirm}
          disabled={!selectedModel}
          className="px-8 py-4 rounded-xl font-bold text-base disabled:cursor-not-allowed flex items-center gap-3 shadow-md hover:shadow-lg"
          style={{
            backgroundColor: selectedModel ? 'var(--lancaster-red)' : 'var(--lancaster-border)',
            color: selectedModel ? 'var(--lancaster-white)' : 'var(--lancaster-text-tertiary)',
            transform: selectedModel ? 'scale(1)' : 'scale(0.98)',
            opacity: selectedModel ? 1 : 0.6
          }}
          onMouseEnter={(e) => {
            if (selectedModel) {
              e.target.style.backgroundColor = 'var(--lancaster-red-dark)'
              e.target.style.transform = 'scale(1.05)'
            }
          }}
          onMouseLeave={(e) => {
            if (selectedModel) {
              e.target.style.backgroundColor = 'var(--lancaster-red)'
              e.target.style.transform = 'scale(1)'
            }
          }}
        >
          <span>Continue with Selected Model</span>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default ModelComparison
