import { useState, useEffect, useCallback } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const BUILTIN_EXAMPLES = [
  { tag: 'groupby', text: 'Group sales by month and calculate total revenue' },
  { tag: 'merge', text: 'Merge two CSVs on user_id and drop duplicates' },
  { tag: 'viz', text: 'Create a heatmap of the correlation matrix' },
  { tag: 'datetime', text: 'Add a column for day of week and flag weekend rows' },
  { tag: 'filter', text: 'Keep only the top 10 customers by total spend' },
  { tag: 'missing', text: 'Show count and percentage of missing values per column' },
  { tag: 'string', text: 'Extract the domain from email addresses and count occurrences' },
  { tag: 'window', text: 'Calculate 7-day rolling average of daily sales' },
]

export default function App() {
  const [description, setDescription] = useState('')
  const [schemaHint, setSchemaHint] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [quota, setQuota] = useState(null)
  const [copied, setCopied] = useState(false)

  const generate = useCallback(async () => {
    if (description.trim().length < 3) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const resp = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, schema_hint: schemaHint || undefined }),
      })
      const data = await resp.json()
      if (!resp.ok) throw new Error(data.detail || 'Request failed')
      setResult(data)
      setQuota(data.remaining_quota)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [description, schemaHint])

  const copyCode = useCallback(() => {
    if (!result?.code) return
    navigator.clipboard.writeText(result.code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }, [result])

  const useExample = (text) => {
    setDescription(text)
    setResult(null)
    setError('')
  }

  return (
    <div className="app">
      <header className="header">
        <h1><span className="leaf">🌿</span> PandasAI</h1>
        <p>Know your data's shape. Describe what you want in English. Get pandas code that runs first-try — column names, dtypes, and all.</p>
      </header>

      <div className="layout">
        {/* Examples sidebar */}
        <aside className="sidebar">
          <h3>Try an example</h3>
          {BUILTIN_EXAMPLES.map((ex) => (
            <button key={ex.text} className="example-btn" onClick={() => useExample(ex.text)}>
              <span className="example-tag">{ex.tag}</span>
              <br />
              {ex.text}
            </button>
          ))}
        </aside>

        {/* Main panel */}
        <main className="panel">
          <div className="field">
            <label htmlFor="desc">What do you want to do?</label>
            <textarea
              id="desc"
              className="description"
              placeholder="e.g. Group sales by month and calculate total revenue"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) generate()
              }}
            />
          </div>

          <div className="field">
            <label htmlFor="schema">Your column names &amp; dtypes <span className="hint">(boosts accuracy — the code knows your data)</span></label>
            <input
              id="schema"
              type="text"
              placeholder="e.g. date(str), revenue(float), region(str)"
              value={schemaHint}
              onChange={(e) => setSchemaHint(e.target.value)}
            />
          </div>

          <button className="generate-btn" onClick={generate} disabled={loading || description.trim().length < 3}>
            {loading ? <><span className="spinner" /> Generating…</> : 'Generate code 🌱'}
          </button>

          {/* Output */}
          {error && <div className="status err">⚠ {error}</div>}

          {result && (
            <div className="output">
              <div className="output-header">
                <h3>Generated code</h3>
                <button className="copy-btn" onClick={copyCode}>
                  {copied ? '✓ Copied' : 'Copy'}
                </button>
              </div>
              <div className="code-block">
                <SyntaxHighlighter language="python" style={oneDark} customStyle={{ background: 'transparent', margin: 0 }}>
                  {result.code}
                </SyntaxHighlighter>
              </div>

              {result.is_valid ? (
                <div className="status ok">✓ Syntax valid · provider: {result.provider}</div>
              ) : (
                <div className="status err">✗ Syntax error: {result.syntax_error}</div>
              )}

              {result.safety_warnings?.length > 0 && (
                <div className="status warn">
                  ⚠ Safety: {result.safety_warnings.join(', ')}
                </div>
              )}
            </div>
          )}

          {quota !== null && (
            <div className="quota">Free-tier queries remaining today: {quota}</div>
          )}
        </main>
      </div>

      <footer className="footer">
        <p>PandasAI · <a href="https://github.com/473185670">open source</a> · free tier: 5 queries/day</p>
      </footer>
    </div>
  )
}
