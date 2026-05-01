import { useEffect, useState } from 'react'
import { getAggregates, getHistory } from '../api.js'

const METRIC_LABELS = {
  faithfulness: 'Faithfulness',
  response_relevancy: 'Response Relevancy',
  context_precision: 'Context Precision',
}

function scoreColor(score) {
  if (score == null) return { emoji: '⚪', color: '#9ca3af' }
  if (score > 0.8) return { emoji: '🟢', color: '#22c55e' }
  if (score >= 0.5) return { emoji: '🟡', color: '#eab308' }
  return { emoji: '🔴', color: '#ef4444' }
}

const fmt = (s) => (s == null ? '—' : s.toFixed(2))

export default function EvalPanel({ latest, historyVersion }) {
  const [history, setHistory] = useState([])
  const [aggregates, setAggregates] = useState({})

  useEffect(() => {
    getHistory().then((d) => setHistory(d.history || [])).catch(() => {})
    getAggregates().then((d) => setAggregates(d.aggregates || {})).catch(() => {})
  }, [historyVersion])

  return (
    <section className="panel eval">
      <h2>📊 Evaluation</h2>

      {latest ? (
        <div className="current-scores">
          <h3>Latest query</h3>
          {Object.keys(METRIC_LABELS).map((key) => {
            const s = latest.scores?.[key]
            const { emoji, color } = scoreColor(s)
            return (
              <div key={key} className="metric-row">
                <span className="metric-label">{METRIC_LABELS[key]}</span>
                <span className="metric-value" style={{ color }}>
                  {emoji} {fmt(s)}
                </span>
              </div>
            )
          })}
        </div>
      ) : (
        <p className="muted">Ask a question to see scores.</p>
      )}

      {Object.keys(aggregates).length > 0 && (
        <div className="aggregates">
          <h3>Aggregates ({history.length} queries)</h3>
          <table>
            <thead>
              <tr>
                <th>Metric</th>
                <th>Mean</th>
                <th>Min</th>
                <th>Max</th>
                <th>N</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(aggregates).map(([key, agg]) => (
                <tr key={key}>
                  <td>{METRIC_LABELS[key] || key}</td>
                  <td>{agg.mean.toFixed(2)}</td>
                  <td>{agg.min.toFixed(2)}</td>
                  <td>{agg.max.toFixed(2)}</td>
                  <td>{agg.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {history.length > 0 && (
        <div className="history">
          <h3>History</h3>
          <details>
            <summary>{history.length} past queries</summary>
            <ul>
              {history
                .slice()
                .reverse()
                .map((entry, i) => (
                  <li key={i}>
                    <div><strong>Q:</strong> {entry.question}</div>
                    <div className="history-scores">
                      {Object.keys(METRIC_LABELS).map((key) => {
                        const s = entry.scores?.[key]
                        const { emoji } = scoreColor(s)
                        return (
                          <span key={key} className="history-score">
                            {emoji} {fmt(s)}
                          </span>
                        )
                      })}
                    </div>
                  </li>
                ))}
            </ul>
          </details>
        </div>
      )}
    </section>
  )
}
