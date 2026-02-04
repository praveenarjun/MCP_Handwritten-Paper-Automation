import { useState } from 'react'
import UploadCard from './components/UploadCard'
import ReportView from './components/ReportView'
import { Zap, Loader2 } from 'lucide-react'

function App() {
  const [answerSheet, setAnswerSheet] = useState(null)

  const [qpFile, setQpFile] = useState(null)
  const [qpText, setQpText] = useState("")

  const [solFile, setSolFile] = useState(null)
  const [solText, setSolText] = useState("")

  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const handleEvaluate = async () => {
    if (!answerSheet) {
      setError("Please upload an Answer Sheet.")
      return
    }
    if (!qpFile && !qpText) {
      setError("Please provide Question Paper (File or Text).")
      return
    }
    if (!solFile && !solText) {
      setError("Please provide Solution Key (File or Text).")
      return
    }

    setLoading(true)
    setError(null)
    setReport(null)

    const formData = new FormData()
    formData.append('answer_sheet', answerSheet)
    if (qpFile) formData.append('question_paper', qpFile)
    if (qpText) formData.append('question_paper_text', qpText)
    if (solFile) formData.append('solution_key', solFile)
    if (solText) formData.append('solution_key_text', solText)

    try {
      const response = await fetch('/api/evaluate', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || "Evaluation failed")
      }

      const data = await response.json()
      setReport(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem', paddingTop: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
          <Zap size={48} color="var(--accent-color)" style={{ filter: 'drop-shadow(0 0 10px var(--accent-glow))' }} />
          <span style={{ background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            MCP Evaluator
          </span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
          Automated handwritten answer sheet evaluation powered by multi-agent AI.
        </p>
      </header>

      <main>
        {/* Input Section */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <UploadCard
            title="1. Answer Sheet"
            accept="image/*, application/pdf"
            onFileSelect={setAnswerSheet}
            type="main"
          />
          <UploadCard
            title="2. Question Paper"
            accept="application/pdf"
            onFileSelect={setQpFile}
            onTextChange={setQpText}
            textValue={qpText}
            textPlaceholder="Paste Question Paper Text..."
          />
          <UploadCard
            title="3. Solution Key"
            accept="application/pdf"
            onFileSelect={setSolFile}
            onTextChange={setSolText}
            textValue={solText}
            textPlaceholder={`{"1": {"text": "...", "marks": 5}}`}
          />
        </div>

        {/* Action Section */}
        <div style={{ textAlign: 'center', margin: '3rem 0' }}>
          {error && (
            <div style={{
              color: 'var(--danger)',
              background: 'rgba(248, 113, 113, 0.1)',
              padding: '1rem',
              borderRadius: '0.5rem',
              display: 'inline-block',
              marginBottom: '1rem',
              border: '1px solid var(--danger)'
            }}>
              {error}
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={handleEvaluate}
            disabled={loading}
            style={{ fontSize: '1.25rem', padding: '1rem 3rem', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" /> Processing...
              </>
            ) : (
              <>Run Evaluation <Zap size={20} fill="currentColor" /></>
            )}
          </button>
        </div>

        {/* Results Section */}
        {report && <ReportView report={report} />}
      </main>

      {/* Footer */}
      <footer style={{ textAlign: 'center', marginTop: '5rem', color: 'var(--text-secondary)', opacity: 0.5, fontSize: '0.9rem' }}>
        <p>&copy; 2026 MCP Answer Evaluator. Built with React & FastAPI.</p>
      </footer>
    </div>
  )
}

export default App
