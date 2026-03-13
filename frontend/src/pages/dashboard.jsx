import React, { useState, useEffect } from "react"
import { apiRequest } from "../api"

const PLATFORMS = [
  { key: "ps",     label: "PlayStation", color: "#0070cc", emoji: "🎮" },
  { key: "steam",  label: "Steam",       color: "#1b2838", emoji: "🖥️" },
  { key: "switch", label: "Nintendo Switch", color: "#e4000f", emoji: "🕹️" },
  { key: "switch2", label: "Nintendo Switch 2", color: "#c40027", emoji: "🆕" },
  { key: "xbox",   label: "Xbox",        color: "#107c10", emoji: "🟩" },
]

export default function Dashboard({ token, onLogout }) {
  const [user, setUser]               = useState(null)
  const [wishlist, setWishlist]       = useState([])
  const [newGame, setNewGame]         = useState("")
  const [pushover, setPushover]       = useState("")
  const [notifyEmail, setNotifyEmail] = useState("")
  const [selectedPlatforms, setSelectedPlatforms] = useState(["ps"])
  const [error, setError]             = useState("")
  const [success, setSuccess]         = useState("")
  const [loading, setLoading]         = useState(false)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [userData, wishlistData] = await Promise.all([
        apiRequest("/auth/me", {}, token),
        apiRequest("/wishlist/", {}, token),
      ])
      setUser(userData)
      setWishlist(wishlistData)
      setPushover(userData.pushover_key || "")
      setNotifyEmail(userData.notification_email || "")
      // Parse platforms string "ps,steam" → ["ps", "steam"]
      setSelectedPlatforms((userData.platforms || "ps").split(",").map(p => p.trim()))
    } catch (e) {
      setError(e.message)
    }
  }

  const togglePlatform = (key) => {
    setSelectedPlatforms(prev =>
      prev.includes(key)
        ? prev.filter(p => p !== key)
        : [...prev, key]
    )
  }

  const addGame = async () => {
    if (!newGame.trim()) return
    setError("")
    try {
      const item = await apiRequest("/wishlist/", {
        method: "POST",
        body: JSON.stringify({ game_title: newGame.trim() }),
      }, token)
      setWishlist([...wishlist, item])
      setNewGame("")
      showSuccess("Game added to wishlist!")
    } catch (e) {
      setError(e.message)
    }
  }

  const removeGame = async (id, title) => {
    try {
      await apiRequest(`/wishlist/${id}`, { method: "DELETE" }, token)
      setWishlist(wishlist.filter(item => item.id !== id))
      showSuccess(`Removed "${title}"`)
    } catch (e) {
      setError(e.message)
    }
  }

  const saveSettings = async () => {
    if (selectedPlatforms.length === 0) {
      setError("Please select at least one platform.")
      return
    }
    setLoading(true)
    setError("")
    try {
      await apiRequest("/auth/me", {
        method: "PUT",
        body: JSON.stringify({
          pushover_key:       pushover      || null,
          notification_email: notifyEmail   || null,
          platforms:          selectedPlatforms.join(","),
        }),
      }, token)
      showSuccess("Settings saved!")
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const showSuccess = (msg) => {
    setSuccess(msg)
    setTimeout(() => setSuccess(""), 3000)
  }

  return (
    <div style={styles.container}>
      <div style={styles.inner}>

        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>🎮 Game Deals</h1>
          <div style={styles.headerRight}>
            <span style={styles.emailText}>{user?.email}</span>
            <button style={styles.logoutBtn} onClick={onLogout}>Logout</button>
          </div>
        </div>

        {error   && <div style={styles.error}>{error}</div>}
        {success && <div style={styles.successMsg}>{success}</div>}

        {/* Wishlist */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>🎯 Your Wishlist</h2>
          <p style={styles.cardSubtitle}>You'll get notified when any of these games go on sale across your selected platforms.</p>

          <div style={styles.addRow}>
            <input
              style={styles.input}
              type="text"
              placeholder="Add a game (e.g. Elden Ring)"
              value={newGame}
              onChange={e => setNewGame(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addGame()}
            />
            <button style={styles.addBtn} onClick={addGame}>Add</button>
          </div>

          {wishlist.length === 0 ? (
            <p style={styles.empty}>No games yet — add some above!</p>
          ) : (
            <ul style={styles.list}>
              {wishlist.map(item => (
                <li key={item.id} style={styles.listItem}>
                  <span style={styles.gameName}>🎮 {item.game_title}</span>
                  <button style={styles.removeBtn} onClick={() => removeGame(item.id, item.game_title)}>
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Notification Settings */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>🔔 Notification Settings</h2>
          <p style={styles.cardSubtitle}>Choose where and how you receive deal alerts.</p>

          {/* Platform Selection */}
          <label style={styles.label}>Platforms to Monitor</label>
          <div style={styles.platformGrid}>
            {PLATFORMS.map(p => {
              const active = selectedPlatforms.includes(p.key)
              return (
                <button
                  key={p.key}
                  onClick={() => togglePlatform(p.key)}
                  style={{
                    ...styles.platformBtn,
                    background:  active ? p.color : "#0f3460",
                    border:      active ? `2px solid ${p.color}` : "2px solid #333",
                    opacity:     active ? 1 : 0.5,
                  }}
                >
                  <span style={styles.platformEmoji}>{p.emoji}</span>
                  <span style={styles.platformLabel}>{p.label}</span>
                  {active && <span style={styles.checkmark}>✓</span>}
                </button>
              )
            })}
          </div>
          <p style={styles.hint}>Select all platforms you want to monitor for deals.</p>

          {/* Notification Email */}
          <label style={styles.label}>Notification Email</label>
          <input
            style={styles.input}
            type="email"
            placeholder={`Leave blank to use ${user?.email || "your login email"}`}
            value={notifyEmail}
            onChange={e => setNotifyEmail(e.target.value)}
          />
          <p style={styles.hint}>Send deal alerts to a different email than your login email.</p>

          {/* Pushover */}
          <label style={styles.label}>Pushover User Key</label>
          <input
            style={styles.input}
            type="text"
            placeholder="Pushover User Key (optional)"
            value={pushover}
            onChange={e => setPushover(e.target.value)}
          />
          <p style={styles.hint}>
            Get your key at{" "}
            <a href="https://pushover.net" target="_blank" rel="noreferrer" style={styles.link}>
              pushover.net
            </a>
            {" "}— $5 one-time fee for phone push notifications.
          </p>

          <button style={styles.saveBtn} onClick={saveSettings} disabled={loading}>
            {loading ? "Saving..." : "Save Settings"}
          </button>
        </div>

      </div>
    </div>
  )
}

const styles = {
  container:    { minHeight: "100vh", background: "#1a1a2e", padding: "2rem" },
  inner:        { maxWidth: "700px", margin: "0 auto" },
  header:       { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" },
  title:        { color: "#fff", fontSize: "1.8rem", margin: 0 },
  headerRight:  { display: "flex", alignItems: "center", gap: "1rem" },
  emailText:    { color: "#aaa", fontSize: "0.9rem" },
  logoutBtn:    { background: "transparent", border: "1px solid #555", borderRadius: "6px", color: "#aaa", padding: "0.4rem 0.8rem", cursor: "pointer" },
  card:         { background: "#16213e", borderRadius: "12px", padding: "1.5rem", marginBottom: "1.5rem" },
  cardTitle:    { color: "#fff", marginTop: 0, marginBottom: "0.25rem" },
  cardSubtitle: { color: "#888", fontSize: "0.9rem", marginBottom: "1.25rem" },
  addRow:       { display: "flex", gap: "0.75rem", marginBottom: "1rem" },
  input:        { width: "100%", padding: "0.75rem", marginBottom: "0.75rem", background: "#0f3460", border: "1px solid #333", borderRadius: "8px", color: "#fff", fontSize: "1rem", boxSizing: "border-box" },
  addBtn:       { padding: "0.75rem 1.25rem", background: "#0070cc", border: "none", borderRadius: "8px", color: "#fff", fontWeight: "bold", cursor: "pointer", whiteSpace: "nowrap" },
  saveBtn:      { padding: "0.75rem 1.5rem", background: "#0070cc", border: "none", borderRadius: "8px", color: "#fff", fontWeight: "bold", cursor: "pointer", marginTop: "0.5rem" },
  list:         { listStyle: "none", padding: 0, margin: 0 },
  listItem:     { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", borderBottom: "1px solid #1a1a2e" },
  gameName:     { color: "#eee" },
  removeBtn:    { background: "transparent", border: "1px solid #ff4444", borderRadius: "6px", color: "#ff6b6b", padding: "0.3rem 0.6rem", cursor: "pointer", fontSize: "0.85rem" },
  empty:        { color: "#555", textAlign: "center", padding: "1rem" },
  error:        { background: "#ff000033", border: "1px solid #ff4444", borderRadius: "8px", padding: "0.75rem", color: "#ff6b6b", marginBottom: "1rem" },
  successMsg:   { background: "#00c85333", border: "1px solid #00c853", borderRadius: "8px", padding: "0.75rem", color: "#00c853", marginBottom: "1rem" },
  label:        { color: "#aaa", fontSize: "0.85rem", display: "block", marginBottom: "0.75rem" },
  hint:         { color: "#666", fontSize: "0.8rem", marginTop: "-0.25rem", marginBottom: "1rem" },
  link:         { color: "#0070cc" },
  platformGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginBottom: "1rem" },
  platformBtn:  { display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.75rem 1rem", borderRadius: "8px", color: "#fff", cursor: "pointer", fontSize: "0.95rem", transition: "all 0.2s", position: "relative" },
  platformEmoji:{ fontSize: "1.2rem" },
  platformLabel:{ fontWeight: "bold" },
  checkmark:    { marginLeft: "auto", fontSize: "0.9rem", color: "#fff" },
}