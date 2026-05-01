async function parseError(res) {
  try {
    const body = await res.json()
    return body.detail || body.error || `HTTP ${res.status}`
  } catch {
    return `HTTP ${res.status}`
  }
}

export async function ingest(files) {
  const formData = new FormData()
  for (const f of files) formData.append('files', f)
  const res = await fetch('/api/ingest', { method: 'POST', body: formData })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function query(question, mode) {
  const res = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, mode }),
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function getStatus() {
  const res = await fetch('/api/status')
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function getHistory() {
  const res = await fetch('/api/history')
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function getAggregates() {
  const res = await fetch('/api/aggregates')
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}
