/**
 * InputPage.jsx
 * Owner: Hira (Frontend Lead)
 * Week:  Week 1 — functional skeleton (no styling yet)
 *
 * What this page does:
 *   - Lets the user paste Python code OR enter a GitHub URL
 *   - Sends it to the Flask /analyze endpoint
 *   - Shows the raw JSON response (placeholder until Dashboard is built in Week 5)
 *
 * TODO Week 2: add tab switching between "Paste Code" and "GitHub URL" modes
 * TODO Week 5: replace <pre> JSON dump with the real Dashboard component
 */

import { useState } from 'react'
import axios from 'axios'

const API_BASE = '/api'   // proxied to http://localhost:5000 via vite.config.js

export default function InputPage() {
  const [code,      setCode]      = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [result,    setResult]    = useState(null)
  const [error,     setError]     = useState(null)
  const [loading,   setLoading]   = useState(false)

  // Which input mode the user has selected
  const [mode, setMode] = useState('code')   // 'code' | 'github'

  const handleSubmit = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    const body = mode === 'code'
      ? { code }
      : { github_url: githubUrl }

    try {
      const res = await axios.post(`${API_BASE}/analyze`, body)
      setResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.error || 'Something went wrong. Is the backend running?'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', padding: '0 20px', fontFamily: 'sans-serif' }}>

      <h1>Code Quality Analyzer</h1>
      <p style={{ color: '#666' }}>Paste Python code or provide a GitHub repo URL to analyse.</p>

      {/* Mode toggle */}
      <div style={{ marginBottom: 16 }}>
        <button onClick={() => setMode('code')}   disabled={mode === 'code'}  style={{ marginRight: 8 }}>Paste Code</button>
        <button onClick={() => setMode('github')} disabled={mode === 'github'}>GitHub URL</button>
      </div>

      {/* Code paste input */}
      {mode === 'code' && (
        <textarea
          rows={16}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 13, padding: 12, boxSizing: 'border-box' }}
          placeholder="# Paste your Python code here..."
          value={code}
          onChange={e => setCode(e.target.value)}
        />
      )}

      {/* GitHub URL input */}
      {mode === 'github' && (
        <input
          type="url"
          style={{ width: '100%', padding: 12, fontSize: 14, boxSizing: 'border-box' }}
          placeholder="https://github.com/username/repository"
          value={githubUrl}
          onChange={e => setGithubUrl(e.target.value)}
        />
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{ marginTop: 12, padding: '10px 24px', fontSize: 15, cursor: loading ? 'wait' : 'pointer' }}
      >
        {loading ? 'Analysing…' : 'Analyse'}
      </button>

      {/* Error display */}
      {error && (
        <div style={{ marginTop: 20, padding: 16, background: '#fff0f0', border: '1px solid #f5c6cb', borderRadius: 6, color: '#721c24' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Result display — raw JSON for now, Dashboard in Week 5 */}
      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>Result (raw — Dashboard coming Week 5)</h2>
          <p>Quality Score: <strong>{result.score}</strong> / 100</p>
          <pre style={{
            background: '#1a1a2e', color: '#c9e0f0', padding: 16,
            borderRadius: 8, overflowX: 'auto', fontSize: 12, lineHeight: 1.6
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

    </div>
  )
}
