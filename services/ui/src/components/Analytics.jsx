import { useState, useEffect } from 'react'

function Analytics() {
  const [summary, setSummary] = useState(null)
  const [recentQueries, setRecentQueries] = useState([])
  const [popularQueries, setPopularQueries] = useState([])
  const [modelStats, setModelStats] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalytics()
    // Refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)

      // Get user_id from localStorage
      const userId = localStorage.getItem('user_id')
      if (!userId) {
        setError('User not authenticated')
        setLoading(false)
        return
      }

      const [summaryRes, recentRes, popularRes, statsRes] = await Promise.all([
        fetch(`/api/analytics/summary?user_id=${userId}`),
        fetch(`/api/analytics/recent-queries?user_id=${userId}&limit=10`),
        fetch(`/api/analytics/popular-queries?user_id=${userId}&limit=5`),
        fetch(`/api/analytics/model-stats?user_id=${userId}`)
      ])

      setSummary(await summaryRes.json())
      setRecentQueries(await recentRes.json())
      setPopularQueries(await popularRes.json())
      setModelStats(await statsRes.json())
      setError(null)
    } catch (err) {
      setError('Failed to load analytics data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div
            className="w-16 h-16 border-4 border-t-transparent rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'var(--lancaster-red)', borderTopColor: 'transparent' }}
          />
          <p style={{ color: 'var(--lancaster-text-secondary)' }}>Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p style={{ color: 'var(--lancaster-text-secondary)' }}>{error}</p>
          <button
            onClick={fetchAnalytics}
            className="mt-4 px-4 py-2 rounded-lg"
            style={{
              backgroundColor: 'var(--lancaster-red)',
              color: 'var(--lancaster-white)'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--lancaster-text-primary)' }}>
          Analytics Dashboard
        </h1>
        <p style={{ color: 'var(--lancaster-text-secondary)' }}>
          User interaction metrics and model performance
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Queries"
          value={summary?.total_queries || 0}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
        />
        <StatCard
          title="Avg Response Time"
          value={`${summary?.avg_latency_ms?.toFixed(0) || 0}ms`}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Avg Citations"
          value={summary?.avg_citations_per_response?.toFixed(1) || 0}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />
        <StatCard
          title="Comparisons"
          value={summary?.total_comparisons || 0}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Queries */}
        <div
          className="border rounded-xl p-6"
          style={{
            backgroundColor: 'var(--lancaster-white)',
            borderColor: 'var(--lancaster-border)'
          }}
        >
          <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--lancaster-text-primary)' }}>
            Recent Queries
          </h2>
          <div className="space-y-3">
            {recentQueries.length === 0 ? (
              <p style={{ color: 'var(--lancaster-text-tertiary)' }}>No queries yet</p>
            ) : (
              recentQueries.map((q, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border"
                  style={{
                    backgroundColor: 'var(--lancaster-bg)',
                    borderColor: 'var(--lancaster-border)'
                  }}
                >
                  <p className="text-sm mb-1" style={{ color: 'var(--lancaster-text-primary)' }}>
                    {q.query}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--lancaster-text-tertiary)' }}>
                    {new Date(q.timestamp).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Popular Queries */}
        <div
          className="border rounded-xl p-6"
          style={{
            backgroundColor: 'var(--lancaster-white)',
            borderColor: 'var(--lancaster-border)'
          }}
        >
          <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--lancaster-text-primary)' }}>
            Popular Queries
          </h2>
          <div className="space-y-3">
            {popularQueries.length === 0 ? (
              <p style={{ color: 'var(--lancaster-text-tertiary)' }}>No data yet</p>
            ) : (
              popularQueries.map((q, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <p className="text-sm flex-1" style={{ color: 'var(--lancaster-text-primary)' }}>
                    {q.query}
                  </p>
                  <span
                    className="px-3 py-1 rounded-full text-xs font-semibold ml-2"
                    style={{
                      backgroundColor: 'var(--lancaster-red)',
                      color: 'var(--lancaster-white)'
                    }}
                  >
                    {q.count}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Model Stats */}
      <div
        className="border rounded-xl p-6"
        style={{
          backgroundColor: 'var(--lancaster-white)',
          borderColor: 'var(--lancaster-border)'
        }}
      >
        <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--lancaster-text-primary)' }}>
          Model Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {modelStats.map((model) => (
            <div
              key={model.model_id}
              className="p-4 rounded-lg border"
              style={{
                backgroundColor: 'var(--lancaster-bg)',
                borderColor: 'var(--lancaster-border)'
              }}
            >
              <h3 className="font-semibold mb-3" style={{ color: 'var(--lancaster-text-primary)' }}>
                {model.model_id.split('/')[1]}
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span style={{ color: 'var(--lancaster-text-secondary)' }}>Queries:</span>
                  <span style={{ color: 'var(--lancaster-text-primary)' }} className="font-semibold">
                    {model.total_queries}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: 'var(--lancaster-text-secondary)' }}>Avg Latency:</span>
                  <span style={{ color: 'var(--lancaster-text-primary)' }} className="font-semibold">
                    {model.avg_latency_ms.toFixed(0)}ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: 'var(--lancaster-text-secondary)' }}>Citations:</span>
                  <span style={{ color: 'var(--lancaster-text-primary)' }} className="font-semibold">
                    {model.total_citations}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon }) {
  return (
    <div
      className="p-6 rounded-xl border"
      style={{
        backgroundColor: 'var(--lancaster-white)',
        borderColor: 'var(--lancaster-border)',
        boxShadow: 'var(--lancaster-shadow-sm)'
      }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm mb-1" style={{ color: 'var(--lancaster-text-secondary)' }}>
            {title}
          </p>
          <p className="text-2xl font-bold" style={{ color: 'var(--lancaster-text-primary)' }}>
            {value}
          </p>
        </div>
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'var(--lancaster-red)', color: 'var(--lancaster-white)' }}
        >
          {icon}
        </div>
      </div>
    </div>
  )
}

export default Analytics
