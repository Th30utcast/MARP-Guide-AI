function Citation({ citation }) {
  return (
    <a
      href={citation.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded p-3 text-sm transition-colors"
      style={{ backgroundColor: '#2b2d31', borderLeft: '3px solid #3ba55d' }}
      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#32353b'}
      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2b2d31'}
    >
      <div className="flex items-center justify-between gap-4">
        <span className="font-medium text-gray-200 flex-1">
          {citation.title}
        </span>
        <span className="text-gray-400 text-xs whitespace-nowrap">Page {citation.page}</span>
      </div>
    </a>
  )
}

export default Citation
