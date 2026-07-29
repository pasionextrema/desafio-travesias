import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import './pages.css'

interface Trivia {
  id: string
  title: string
  theme: string
  level: string
  unique_code: string
  start_date: string
  end_date: string
  prize_amount: number
  winners_count: number
}

export default function TriviaListPage() {
  const { user } = useAuth()
  const [trivias, setTrivias] = useState<Trivia[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    api.get('/trivias', { params: { level: filter || undefined } })
      .then(({ data }) => setTrivias(data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [filter, user])

  const levelColors: Record<string, string> = {
    explorador: '#4CAF50',
    navegante: '#2196F3',
    constructor: '#9C27B0',
    estrella: '#FFD700',
  }

  if (loading) return <div className="loading">Cargando trivias...</div>

  return (
    <div className="trivia-list-page">
      <h1>Trivias Disponibles</h1>
      <div className="filter-bar">
        {['', 'explorador', 'navegante', 'constructor', 'estrella'].map((l) => (
          <button
            key={l}
            className={`btn btn-small ${filter === l ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setFilter(l)}
          >
            {l ? l.charAt(0).toUpperCase() + l.slice(1) : 'Todas'}
          </button>
        ))}
      </div>

      {trivias.length === 0 ? (
        <p className="text-secondary">No hay trivias disponibles.</p>
      ) : (
        <div className="trivia-grid">
          {trivias.map((t) => (
            <Link to={`/trivia/${t.unique_code}`} key={t.id} className="trivia-card-link">
              <div className="trivia-card" style={{ borderLeft: `4px solid ${levelColors[t.level]}` }}>
                <div className="trivia-card-header">
                  <h3>{t.title}</h3>
                  <span className="trivia-level" style={{ background: levelColors[t.level] }}>{t.level}</span>
                </div>
                {t.theme && <p className="trivia-theme">{t.theme}</p>}
                <div className="trivia-meta">
                  <span>Codigo: <strong>{t.unique_code}</strong></span>
                  <span>Premio: <strong>${t.prize_amount}</strong></span>
                </div>
                <div className="trivia-dates">
                  <span>Inicio: {new Date(t.start_date).toLocaleDateString()}</span>
                  <span>Fin: {new Date(t.end_date).toLocaleDateString()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
