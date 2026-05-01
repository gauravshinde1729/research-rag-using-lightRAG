import { useState } from 'react'
import { query as queryApi } from '../api.js'

function truncate(text, n = 500) {
  if (!text) return ''
  return text.length > n ? text.slice(0, n) + '…' : text
}

export default function ChatPanel({ disabled, mode, onAnswered }) {
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleAsk() {
    if (!question.trim()) return
    setBusy(true)
    setError(null)
    try {
      const r = await queryApi(question, mode)
      setResult(r)
      onAnswered(r)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel chat">
      <h2>💬 Chat</h2>
      <textarea
        rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about your papers…"
        disabled={disabled || busy}
      />
      <button onClick={handleAsk} disabled={disabled || busy || !question.trim()}>
        {busy ? 'Thinking…' : 'Ask'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="answer">
          <h3>Answer</h3>
          <p>{result.answer}</p>
          <details>
            <summary>{result.contexts.length} retrieved context(s)</summary>
            {result.contexts.map((c, i) => (
              <pre key={i} className="context">{truncate(c)}</pre>
            ))}
          </details>
        </div>
      )}
    </section>
  )
}
