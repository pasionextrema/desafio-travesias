import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import './pages.css'

interface QuestionData {
  id: string
  question_type: string
  question_text: { es: string }
  options: any
  time_limit: number
}

interface TriviaSession {
  participation_id: string
  trivia_code: string
  questions: QuestionData[]
}

export default function TriviaPlayerPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [session, setSession] = useState<TriviaSession | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [timeLeft, setTimeLeft] = useState(30)
  const [selected, setSelected] = useState<string | null>(null)
  const [answered, setAnswered] = useState(false)
  const [result, setResult] = useState<{ is_correct: boolean; score: number } | null>(null)
  const [totalScore, setTotalScore] = useState(0)
  const [finished, setFinished] = useState(false)
  const [error, setError] = useState('')
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  useEffect(() => {
    const stored = localStorage.getItem('active_trivia')
    if (stored) {
      const s = JSON.parse(stored) as TriviaSession
      setSession(s)
      if (s.questions.length > 0) {
        setTimeLeft(s.questions[0].time_limit)
      }
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [])

  useEffect(() => {
    if (!session || currentIndex >= session.questions.length) return
    const q = session.questions[currentIndex]
    setTimeLeft(q.time_limit)
    setSelected(null)
    setAnswered(false)
    setResult(null)
    startTimeRef.current = Date.now()

    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          if (timerRef.current) clearInterval(timerRef.current)
          handleTimeUp()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [currentIndex, session])

  async function handleTimeUp() {
    if (answered || !session || !code) return
    setAnswered(true)
    await api.post(`/trivias/${code}/answer`, {
      participation_id: session.participation_id,
      question_id: session.questions[currentIndex].id,
      answer_data: {},
      client_start_ms: startTimeRef.current,
      client_end_ms: Date.now(),
    })
    setResult({ is_correct: false, score: 0 })
  }

  async function handleSelect(optionId: string) {
    if (answered || !session || !code) return
    setSelected(optionId)
    setAnswered(true)
    if (timerRef.current) clearInterval(timerRef.current)
    try {
      const { data } = await api.post(`/trivias/${code}/answer`, {
        participation_id: session.participation_id,
        question_id: session.questions[currentIndex].id,
        answer_data: { selected: optionId },
        client_start_ms: startTimeRef.current,
        client_end_ms: Date.now(),
      })
      setResult({ is_correct: data.is_correct, score: data.score })
      setTotalScore((s) => s + data.score)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error')
    }
  }

  async function handleNext() {
    if (!session) return
    const next = currentIndex + 1
    if (next >= session.questions.length) {
      try {
        const { data } = await api.post(`/trivias/${code}/finish`, {
          participation_id: session.participation_id,
        })
        localStorage.removeItem('active_trivia')
        navigate(`/trivia/${code}/results`, { state: data })
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al finalizar')
      }
    } else {
      setCurrentIndex(next)
    }
  }

  if (!session) return <div className="loading">Cargando trivia...</div>
  if (currentIndex >= session.questions.length) return <div className="loading">Finalizando...</div>

  const question = session.questions[currentIndex]
  const progress = ((currentIndex + 1) / session.questions.length) * 100
  const options = question.options?.options || []
  const timePercent = (timeLeft / question.time_limit) * 100

  return (
    <div className="trivia-player-page">
      <div className="player-header">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="player-info">
          <span>Pregunta {currentIndex + 1} de {session.questions.length}</span>
          <span className={`timer ${timeLeft <= 5 ? 'timer-danger' : ''}`}
            style={{ background: `conic-gradient(var(--accent) ${timePercent}%, transparent 0)` }}>
            {timeLeft}s
          </span>
        </div>
      </div>

      <div className="question-card">
        <h2>{question.question_text?.es || question.question_text}</h2>

        <div className="options-grid">
          {options.map((opt: any) => {
            let cls = 'option-btn'
            if (answered) {
              if (opt.is_correct) cls += ' option-correct'
              else if (selected === opt.id) cls += ' option-wrong'
              else cls += ' option-dimmed'
            } else if (selected === opt.id) {
              cls += ' option-selected'
            }
            return (
              <button
                key={opt.id}
                className={cls}
                onClick={() => handleSelect(opt.id)}
                disabled={answered}
              >
                {opt.text?.es || opt.text}
              </button>
            )
          })}
        </div>

        {result && (
          <div className={`answer-feedback ${result.is_correct ? 'feedback-correct' : 'feedback-wrong'}`}>
            {result.is_correct ? `Correcto! +${result.score} pts` : `Incorrecto (0 pts)`}
          </div>
        )}

        {answered && (
          <button className="btn btn-primary btn-large" onClick={handleNext}>
            {currentIndex + 1 >= session.questions.length ? 'Ver Resultados' : 'Siguiente'}
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}
    </div>
  )
}
