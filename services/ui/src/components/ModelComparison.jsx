import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Citation from './Citation'

function ModelComparisonCard({ result, isSelected, onSelect }) {
  return (
    <div
      onClick={onSelect}
      className={`cursor-pointer rounded-lg p-4 transition-all ${
        isSelected ? 'ring-2' : ''
      }`}
      style={{
        backgroundColor: '#383a40',
        borderLeft: `4px solid ${isSelected ? '#5865f2' : '#3ba55d'}`,
        ...(isSelected && { ringColor: '#5865f2' })
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="font-semibold text-gray-100">{result.model_name}</h3>
          <p className="text-xs text-gray-400">{result.model_id}</p>
        </div>
        {isSelected && (
          <div className="px-3 py-1 rounded text-xs font-medium text-white" style={{ backgroundColor: '#5865f2' }}>
            Selected
          </div>
        )}
      </div>

      <div className="prose prose-sm max-w-none prose-invert mb-3">
        <ReactMarkdown>{result.answer}</ReactMarkdown>
      </div>

      {result.citations && result.citations.length > 0 && (
        <div className="mt-3 space-y-2">
          <p className="text-xs font-semibold text-gray-400">Sources:</p>
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
    <div className="space-y-4">
      <div className="rounded-lg p-4" style={{ backgroundColor: '#2b2d31', borderLeft: '4px solid #5865f2' }}>
        <h2 className="text-lg font-semibold text-gray-100 mb-2">
          Compare 3 AI Models
        </h2>
        <p className="text-sm text-gray-300">
          Your query: <span className="italic">"{comparisonData.query}"</span>
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Select your preferred model to continue the conversation
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {comparisonData.results.map((result) => (
          <ModelComparisonCard
            key={result.model_id}
            result={result}
            isSelected={selectedModel === result.model_id}
            onSelect={() => handleSelect(result.model_id)}
          />
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleConfirm}
          disabled={!selectedModel}
          className="px-6 py-3 text-white rounded-lg transition-colors font-medium disabled:cursor-not-allowed"
          style={{
            backgroundColor: selectedModel ? '#5865f2' : '#2b2d31',
            color: selectedModel ? 'white' : '#6b7280'
          }}
        >
          Continue with Selected Model
        </button>
      </div>
    </div>
  )
}

export default ModelComparison
