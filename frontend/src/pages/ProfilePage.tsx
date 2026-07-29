import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './pages.css'

export default function ProfilePage() {
  const { user, logout, updateProfile } = useAuth()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
    country: user?.country || '',
    nationality: user?.nationality || '',
    instagram_user: user?.instagram_user || '',
    youtube_user: user?.youtube_user || '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const levelColors: Record<string, string> = {
    explorador: '#4CAF50',
    navegante: '#2196F3',
    constructor: '#9C27B0',
    estrella: '#FFD700',
  }

  const levelGems: Record<string, string> = {
    explorador: 'Jade',
    navegante: 'Zafiro',
    constructor: 'Amatista',
    estrella: 'Diamante',
  }

  async function handleSave() {
    setError('')
    setSuccess('')
    try {
      await updateProfile(form)
      setSuccess('Perfil actualizado!')
      setEditing(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar')
    }
  }

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  if (!user) return null

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-header">
          <div
            className="avatar-circle"
            style={{ background: levelColors[user.role] || '#0984E3' }}
          >
            {user.full_name?.[0] || user.email[0].toUpperCase()}
          </div>
          <div>
            <h1>{user.full_name || 'Sin nombre'}</h1>
            <span className="role-badge" style={{ background: levelColors[user.role] }}>
              {user.role} - Gema {levelGems[user.role]}
            </span>
          </div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="profile-fields">
          <div className="field">
            <label>Email</label>
            <span>{user.email}</span>
            {user.email_verified ? (
              <span className="verified">Verificado</span>
            ) : (
              <span className="not-verified">No verificado</span>
            )}
          </div>
          <div className="field">
            <label>Codigo de Referido</label>
            <span className="referral-code">{user.referral_code}</span>
          </div>

          {editing ? (
            <>
              <div className="field">
                <label>Nombre Completo</label>
                <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
              </div>
              <div className="field">
                <label>Nombre de Usuario</label>
                <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
              </div>
              <div className="field">
                <label>Pais de Residencia</label>
                <input value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
              </div>
              <div className="field">
                <label>Nacionalidad</label>
                <input value={form.nationality} onChange={(e) => setForm({ ...form, nationality: e.target.value })} />
              </div>
              <div className="field">
                <label>Usuario de Instagram</label>
                <input value={form.instagram_user} onChange={(e) => setForm({ ...form, instagram_user: e.target.value })} placeholder="sin @" />
              </div>
              <div className="field">
                <label>Usuario de YouTube</label>
                <input value={form.youtube_user} onChange={(e) => setForm({ ...form, youtube_user: e.target.value })} placeholder="sin @" />
              </div>
              <div className="btn-row">
                <button className="btn btn-primary" onClick={handleSave}>Guardar</button>
                <button className="btn btn-secondary" onClick={() => setEditing(false)}>Cancelar</button>
              </div>
            </>
          ) : (
            <>
              <div className="field">
                <label>Nombre Completo</label>
                <span>{user.full_name || '---'}</span>
              </div>
              <div className="field">
                <label>Nombre de Usuario</label>
                <span>{user.username || '---'}</span>
              </div>
              <div className="field">
                <label>Pais</label>
                <span>{user.country || '---'}</span>
              </div>
              <div className="field">
                <label>Nacionalidad</label>
                <span>{user.nationality || '---'}</span>
              </div>
              <button className="btn btn-primary" onClick={() => setEditing(true)}>Editar Perfil</button>
            </>
          )}
        </div>

        <button className="btn btn-danger" onClick={handleLogout} style={{ marginTop: '1rem' }}>
          Cerrar Sesion
        </button>
      </div>
    </div>
  )
}
