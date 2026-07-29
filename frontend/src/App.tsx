import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import './App.css'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading">Cargando...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function GuestRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading">Cargando...</div>
  if (user) return <Navigate to="/perfil" replace />
  return <>{children}</>
}

function HomePage() {
  const { user } = useAuth()
  const levels = [
    { name: 'Explorador', color: '#4CAF50', gem: 'Jade' },
    { name: 'Navegante', color: '#2196F3', gem: 'Zafiro' },
    { name: 'Constructor', color: '#9C27B0', gem: 'Amatista' },
    { name: 'Estrella', color: '#FFD700', gem: 'Diamante' },
  ]

  return (
    <main className="main-home">
      <section className="hero-section">
        <h1>Desafio de Travesias</h1>
        <p className="subtitle">Plataforma gamificada de trivias educativas y de entretenimiento</p>
        {user && (
          <p className="welcome-text">
            Bienvenido, <strong>{user.full_name || user.email}</strong>
            <span className="role-badge" style={{ background: getRoleColor(user.role), marginLeft: '0.5rem' }}>
              {user.role}
            </span>
          </p>
        )}
      </section>

      <section className="levels-section">
        <h2>Niveles de Participacion</h2>
        <div className="levels-grid">
          {levels.map((level) => (
            <div key={level.name} className="level-card" style={{ borderColor: level.color }}>
              <span className="gem" style={{ color: level.color, fontSize: '2rem' }}>&#9670;</span>
              <h3 style={{ color: level.color }}>{level.name}</h3>
              <p>Gema {level.gem}</p>
            </div>
          ))}
        </div>
      </section>

      {!user && (
        <section className="cta-section">
          <a href="/register" className="btn btn-primary btn-large">Comenzar Ahora</a>
        </section>
      )}
    </main>
  )
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    explorador: '#4CAF50',
    navegante: '#2196F3',
    constructor: '#9C27B0',
    estrella: '#FFD700',
  }
  return colors[role] || '#0984E3'
}

function AppContent() {
  return (
    <div className="app">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
        <Route path="/perfil" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  )
}
