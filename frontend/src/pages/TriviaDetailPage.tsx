import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import './pages.css'

interface TriviaDetail {
  id: string
  title: string
  theme: string
  level: string
  unique_code: string
  start_date: string
  end_date: string
  prize_amount: number
  winners_count: number
  total_questions: number
  total_time: number
}

export default function TriviaDetailPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [trivia, setTrivia] = useState<TriviaDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    if (!code) return
    api.get(`/trivias/${code}`)
      .then(({ data }) => setTrivia(data))
      .catch((err) => setError(err.response?.data?.detail || 'Error'))
      .finally(() => setLoading(false))
  }, [code])

  async function handleStart() {
    if (!code) return
    setStarting(true)
    setError('')
    try {
      const { data } = await api.post(`/trivias/${code}/start`)
      localStorage.setItem('active_trivia', JSON.stringify(data))
      navigate(`/trivia/${code}/play`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar')
    } finally {
      setStarting(false)
    }
  }

  if (loading) return <div className="loading">Cargando...</div>
  if (!trivia) return <div className="loading">{error || 'Trivia no encontrada'}</div>

  const levelColors: Record<string, string> = {
    explorador: '#4CAF50',
    navegante: '#2196F3',
    constructor: '#9C27B0',
    estrella: '#FFD700',
  }

  return (
    <div className="trivia-detail-page">
      <div className="detail-card">
        <span className="trivia-level-badge" style={{ background: levelColors[trivia.level] }}>
          {trivia.level}
        </span>
        <h1>{trivia.title}</h1>
        {trivia.theme && <p className="detail-theme">{trivia.theme}</p>}

        <div className="detail-grid">
          <div className="detail-item">
            <label>Preguntas</label>
            <span>{trivia.total_questions}</span>
          </div>
          <div className="detail-item">
            <label>Tiempo Total</label>
            <span>{Math.floor(trivia.total_time / 60)}m {trivia.total_time % 60}s</span>
          </div>
          <div className="detail-item">
            <label>Premio</label>
            <span>${trivia.prize_amount}</span>
          </div>
          <div className="detail-item">
            <label>Ganadores</label>
            <span>{trivia.winners_count}</span>
          </div>
        </div>

        <div className="detail-rules">
          <h3>Reglas:</h3>
          <ul>
            <li>Solo tienes una oportunidad para completar esta trivia</li>
            <li>Las preguntas aparecen en orden aleatorio</li>
            <li>El puntaje desciende 10 puntos por segundo de demora</li>
            <li>Si respondes correctamente a tiempo, obtienes al menos 10% del puntaje base</li>
            <li>Respuesta incorrecta o fuera de tiempo: 0 puntos</li>
          </ul>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <button
          className="btn btn-primary btn-large"
          onClick={handleStart}
          disabled={starting}
          style={{ width: '100%', marginTop: '1rem' }}
        >
          {starting ? 'Iniciando...' : 'Comenzar Trivia'}
        </button>
      </div>
    </div>
  )
}
