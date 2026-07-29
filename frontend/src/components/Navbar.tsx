import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Navbar.css'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Desafio de Travesias</Link>
      <div className="navbar-links">
        {user ? (
          <>
            <Link to="/perfil" className="nav-link">
              <span className="nav-avatar" style={{ background: getRoleColor(user.role) }}>
                {user.full_name?.[0] || user.email[0].toUpperCase()}
              </span>
              {user.full_name || user.email}
            </Link>
            <button onClick={handleLogout} className="btn btn-small btn-outline">Salir</button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-small btn-primary">Iniciar Sesion</Link>
            <Link to="/register" className="btn btn-small btn-outline">Registrarse</Link>
          </>
        )}
      </div>
    </nav>
  )
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    explorador: '#4CAF50',
    navegante: '#2196F3',
    constructor: '#9C27B0',
    estrella: '#FFD700',
    admin: '#E17055',
    colaborador: '#00B894',
  }
  return colors[role] || '#0984E3'
}
