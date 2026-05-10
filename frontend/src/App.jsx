import React, { useState, useEffect } from "react"
import Login from "./pages/Login"
import Signup from "./pages/Signup"
import Dashboard from "./pages/Dashboard"
import Admin from "./pages/Admin"
import { apiRequest } from "./api"

const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL || ""

export default function App() {
  const [page, setPage]   = useState("login")
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [user, setUser]   = useState(null)

  useEffect(() => {
    if (token) {
      loadUser()
    }
  }, [token])

  const loadUser = async () => {
    try {
      const userData = await apiRequest("/auth/me", {}, token)
      setUser(userData)
      setPage(userData.email === ADMIN_EMAIL ? "admin" : "dashboard")
    } catch {
      handleLogout()
    }
  }

  const handleLogin = (newToken) => {
    localStorage.setItem("token", newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
    setPage("login")
  }

  if (token && user) {
    if (user.email === ADMIN_EMAIL) {
      return <Admin token={token} onLogout={handleLogout} />
    }
    return <Dashboard token={token} onLogout={handleLogout} />
  }

  if (page === "signup") {
    return <Signup onSignup={handleLogin} onBack={() => setPage("login")} />
  }

  return <Login onLogin={handleLogin} onSignup={() => setPage("signup")} />
}