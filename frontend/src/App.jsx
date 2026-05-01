import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import ChatPanel from './components/ChatPanel.jsx'
import EvalPanel from './components/EvalPanel.jsx'
import { getStatus } from './api.js'

export default function App() {
  const [ingestedCount, setIngestedCount] = useState(0)
  const [mode, setMode] = useState('hybrid')
  const [latestQuery, setLatestQuery] = useState(null)
  // Bumped on every successful query so EvalPanel re-fetches history/aggregates.
  const [historyVersion, setHistoryVersion] = useState(0)

  useEffect(() => {
    getStatus()
      .then((s) => setIngestedCount(s.ingested_count || 0))
      .catch(() => {})
  }, [])

  return (
    <div className="app">
      <Sidebar
        ingestedCount={ingestedCount}
        mode={mode}
        onModeChange={setMode}
        onIngested={(count) => setIngestedCount((prev) => prev + count)}
      />
      <main className="main">
        <h1>Research Paper Q&amp;A</h1>
        {ingestedCount === 0 && (
          <div className="banner">Upload PDFs in the sidebar to get started.</div>
        )}
        <div className="two-col">
          <ChatPanel
            disabled={ingestedCount === 0}
            mode={mode}
            onAnswered={(result) => {
              setLatestQuery(result)
              setHistoryVersion((v) => v + 1)
            }}
          />
          <EvalPanel latest={latestQuery} historyVersion={historyVersion} />
        </div>
      </main>
    </div>
  )
}
