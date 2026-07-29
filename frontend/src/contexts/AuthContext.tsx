import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '../services/api'

interface User {
  id: string
  email: string
  username: string | null
  full_name: string | null
  role: string
  email_verified: boolean
  referral_code: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string, remember?: boolean) => Promise<void>
  register: (email: string, password: string, referral?: string) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      api.get('/auth/me')
        .then(({ data }) => setUser(data))
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  async function login(email: string, password: string, remember = false) {
    const { data } = await api.post('/auth/login', { email, password, remember_me: remember })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const { data: userData } = await api.get('/auth/me')
    setUser(userData)
  }

  async function register(email: string, password: string, referral?: string) {
    const { data } = await api.post('/auth/register', { email, password, referral_code: referral })
    const loginRes = await api.post('/auth/login', { email, password, remember_me: false })
    localStorage.setItem('access_token', loginRes.data.access_token)
    localStorage.setItem('refresh_token', loginRes.data.refresh_token)
    setUser(data)
  }

  async function logout() {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) await api.post('/auth/logout', { refresh_token: refresh })
    } catch {}
    localStorage.clear()
    setUser(null)
  }

  async function updateProfile(data: Partial<User>) {
    const { data: updated } = await api.put('/users/me', data)
    setUser(updated)
  }

  async function refreshUser() {
    const { data } = await api.get('/auth/me')
    setUser(data)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
