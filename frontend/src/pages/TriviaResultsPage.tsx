import { useLocation, useParams, Link } from 'react-router-dom'
import './pages.css'

interface ResultData {
  total_score: number
  correct_count: number
  incorrect_count: number
  null_count: number
  position: number
  finished: boolean
}

export default function TriviaResultsPage() {
  const { code } = useParams<{ code: string }>()
  const location = useLocation()
  const data = (location.state as ResultData) || {
    total_score: 0,
    correct_count: 0,
    incorrect_count: 0,
    null_count: 0,
    position: 0,
    finished: true,
  }

  const total = data.correct_count + data.incorrect_count + data.null_count
  const pct = total > 0 ? Math.round((data.correct_count / total) * 100) : 0

  return (
    <div className="results-page">
      <div className="results-card">
        <h1>Resultados</h1>

        <div className="score-circle" style={{
          background: `conic-gradient(var(--success) ${pct * 3.6}deg, var(--card) 0)`
        }}>
          <div className="score-inner">
            <span className="score-number">{data.total_score}</span>
            <span className="score-label">Puntos</span>
          </div>
        </div>

        <div className="results-grid">
          <div className="result-item correct">
            <span className="count">{data.correct_count}</span>
            <span className="label">Correctas</span>
          </div>
          <div className="result-item incorrect">
            <span className="count">{data.incorrect_count}</span>
            <span className="label">Incorrectas</span>
          </div>
          <div className="result-item null">
            <span className="count">{data.null_count}</span>
            <span className="label">Sin respuesta</span>
          </div>
        </div>

        {data.position > 0 && (
          <div className="position-badge">
            Posicion: <strong>#{data.position}</strong>
          </div>
        )}

        <p className="results-note">
          Respondiste {data.correct_count} correctas, {data.incorrect_count} incorrectas
          y {data.null_count} nulas o fuera de tiempo.
        </p>

        <div className="results-actions">
          <Link to="/trivias" className="btn btn-primary">Ver mas Trivias</Link>
        </div>
      </div>
    </div>
  )
}
