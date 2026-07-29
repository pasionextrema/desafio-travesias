import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './pages.css'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password, remember)
      navigate('/perfil')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar sesion')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <img src="/img/Logo_DT_Login.webp" alt="Desafio de Travesias" />
        </div>
        <div className="auth-header">
          <p>Inicia sesion para continuar</p>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit} className="auth-form">
          <label htmlFor="email">Email o Usuario</label>
          <input
            id="email"
            type="text"
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
            placeholder="Min 8 caracteres"
            required
          />
          <div className="checkbox-row">
            <label>
              <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
              <span>Recordarme</span>
            </label>
          </div>
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Iniciando...' : 'Iniciar Sesion'}
          </button>
        </form>
        <div className="auth-links">
          <Link to="/forgot-password">Olvidaste tu contrasena?</Link>
          <span>|</span>
          <Link to="/register">Crear cuenta</Link>
        </div>
      </div>
    </div>
  )
}
