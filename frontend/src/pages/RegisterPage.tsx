import { useState, FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './pages.css'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const referral = searchParams.get('ref') || ''

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (password !== confirm) {
      setError('Las contrasenas no coinciden')
      return
    }
    setLoading(true)
    try {
      await register(email, password, referral || undefined)
      setSuccess(true)
      setTimeout(() => navigate('/perfil'), 1500)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrarse')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="alert alert-success">
            <h2>Registro exitoso!</h2>
            <p>Redirigiendo a tu perfil...</p>
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
          <h1>Crear Cuenta</h1>
          <p>Unete a Desafio de Travesias</p>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        {referral && (
          <div className="alert alert-info">
            Te invitaron con el codigo: <strong>{referral}</strong>
          </div>
        )}
        <form onSubmit={handleSubmit} className="auth-form">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
          />
          <label htmlFor="password">Contrasena</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Min 8 caracteres, mayus, minus, num, especial"
            required
          />
          <label htmlFor="confirm">Confirmar Contrasena</label>
          <input
            id="confirm"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="Repite tu contrasena"
            required
          />
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Creando...' : 'Crear Cuenta'}
          </button>
        </form>
        <div className="auth-links">
          <Link to="/login">Ya tienes cuenta? Inicia sesion</Link>
        </div>
      </div>
    </div>
  )
}
