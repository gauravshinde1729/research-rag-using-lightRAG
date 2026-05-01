import { useRef, useState } from 'react'
import { ingest } from '../api.js'

export default function Sidebar({ ingestedCount, mode, onModeChange, onIngested }) {
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  async function handleIngest() {
    if (!files.length) return
    setBusy(true)
    setError(null)
    try {
      const result = await ingest(files)
      onIngested(result.ingested || 0)
      setFiles([])
      if (fileInputRef.current) fileInputRef.current.value = ''
      if (result.errors && result.errors.length) {
        setError(`Some files failed: ${result.errors.map((e) => e.file).join(', ')}`)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <aside className="sidebar">
      <h2>📄 Document Upload</h2>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files || []))}
      />

      <label className="field">
        Query Mode
        <select value={mode} onChange={(e) => onModeChange(e.target.value)}>
          <option value="naive">naive</option>
          <option value="local">local</option>
          <option value="global">global</option>
          <option value="hybrid">hybrid</option>
        </select>
      </label>

      <button onClick={handleIngest} disabled={busy || files.length === 0}>
        {busy ? 'Ingesting…' : '🚀 Ingest Documents'}
      </button>

      {busy && (
        <div className="info">Building knowledge graph… this may take a few minutes.</div>
      )}
      {error && <div className="error">{error}</div>}
      {ingestedCount > 0 && (
        <div className="info">✅ {ingestedCount} document(s) indexed</div>
      )}
    </aside>
  )
}
