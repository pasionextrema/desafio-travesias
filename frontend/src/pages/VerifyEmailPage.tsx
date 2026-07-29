import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../services/api'
import './pages.css'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Token no encontrado en la URL')
      return
    }
    api.get(`/auth/verify-email?token=${token}`)
      .then(() => {
        setStatus('success')
        setMessage('Email verificado exitosamente!')
      })
      .catch((err) => {
        setStatus('error')
        setMessage(err.response?.data?.detail || 'Error al verificar el email')
      })
  }, [token])

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <img src="/img/Logo_DT_Login.webp" alt="Desafio de Travesias" />
        </div>
        <div className="auth-header">
          <h1>Verificacion de Email</h1>
        </div>
        {status === 'loading' && <p className="text-center">Verificando...</p>}
        {status === 'success' && (
          <div className="alert alert-success">
            <h2>Email Verificado!</h2>
            <p>{message}</p>
          </div>
        )}
        {status === 'error' && (
          <div className="alert alert-error">
            <p>{message}</p>
          </div>
        )}
        <div className="auth-links">
          <Link to="/login">Ir al login</Link>
        </div>
      </div>
    </div>
  )
}
