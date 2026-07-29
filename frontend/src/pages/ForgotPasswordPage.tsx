import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import './pages.css'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/forgot-password', { email })
      setSent(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="alert alert-success">
            <h2>Email enviado</h2>
            <p>Revisa tu bandeja de entrada para restablecer tu contraseña.</p>
          </div>
          <div className="auth-links">
            <Link to="/login">Volver al inicio de sesion</Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <img src="/img/Logo_DT_Login.webp" alt="Desafio de Travesias" />
        </div>
        <div className="auth-header">
          <h1>Recuperar Contraseña</h1>
          <p>Te enviaremos un enlace a tu email</p>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit} className="auth-form">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Enviando...' : 'Enviar Enlace'}
          </button>
        </form>
        <div className="auth-links">
          <Link to="/login">Volver al login</Link>
        </div>
      </div>
    </div>
  )
}
