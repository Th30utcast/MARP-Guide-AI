function ModelSelector({ onModelSelect, onCancel }) {
  const models = [
    {
      id: 'openai/gpt-4o-mini',
      name: 'GPT-4o Mini',
      description: 'Fast and efficient for most queries'
    },
    {
      id: 'google/gemma-3n-e2b-it:free',
      name: 'Google Gemma 3n 2B',
      description: 'Lightweight and quick responses'
    },
    {
      id: 'deepseek/deepseek-chat',
      name: 'DeepSeek Chat',
      description: 'Detailed and comprehensive answers'
    }
  ]

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              boxShadow: 'var(--lancaster-shadow-md)'
            }}
          >
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
          <h2
            className="text-2xl font-bold mb-2"
            style={{ color: 'var(--lancaster-text-primary)' }}
          >
            Select AI Model
          </h2>
          <p
            className="text-sm"
            style={{ color: 'var(--lancaster-text-secondary)' }}
          >
            Choose which model you'd like to use for answering your questions
          </p>
        </div>

        <div className="space-y-3">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => onModelSelect(model.id)}
              className="w-full text-left p-4 rounded-xl border-2 transition-all"
              style={{
                backgroundColor: 'var(--lancaster-white)',
                borderColor: 'var(--lancaster-border)',
                boxShadow: 'var(--lancaster-shadow-sm)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--lancaster-red)'
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = 'var(--lancaster-shadow-md)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--lancaster-border)'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'var(--lancaster-shadow-sm)'
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold"
                  style={{ backgroundColor: 'var(--lancaster-red)' }}
                >
                  AI
                </div>
                <div className="flex-1">
                  <h3
                    className="font-semibold mb-1"
                    style={{ color: 'var(--lancaster-text-primary)' }}
                  >
                    {model.name}
                  </h3>
                  <p
                    className="text-xs"
                    style={{ color: 'var(--lancaster-text-tertiary)' }}
                  >
                    {model.description}
                  </p>
                </div>
                <svg
                  className="w-5 h-5 flex-shrink-0"
                  fill="none"
                  stroke="var(--lancaster-red)"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          ))}
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="mt-4 w-full p-3 rounded-xl text-sm font-semibold"
            style={{
              backgroundColor: 'var(--lancaster-bg)',
              color: 'var(--lancaster-text-secondary)',
              border: '1px solid var(--lancaster-border)'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--lancaster-white)'
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'var(--lancaster-bg)'
            }}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}

export default ModelSelector
