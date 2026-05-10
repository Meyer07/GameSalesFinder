import React, { useState, useEffect } from "react"
import { apiRequest } from "../api"

const PLATFORMS = [
  { key: "ps",   label: "PlayStation" },
  { key: "xbox", label: "Xbox" },
]

export default function Admin({ token, onLogout }) {
  const [deals, setDeals]         = useState([])
  const [platform, setPlatform]   = useState("ps")
  const [error, setError]         = useState("")
  const [success, setSuccess]     = useState("")
  const [loading, setLoading]     = useState(false)
  const [showForm, setShowForm]   = useState(false)

  const [form, setForm] = useState({
    game_title:    "",
    platform:      "ps",
    sale_price:    "",
    regular_price: "",
    discount:      "",
    url:           "",
    sale_end_date: "",
  })

  useEffect(() => { loadDeals() }, [platform])

  const loadDeals = async () => {
    try {
      const data = await apiRequest(`/deals/?platform=${platform}`, {}, token)
      setDeals(data)
    } catch (e) {
      setError(e.message)
    }
  }

  const handleFormChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))

    // Auto-calculate discount when prices change
    if (field === "sale_price" || field === "regular_price") {
      const sale    = field === "sale_price"    ? parseFloat(value) : parseFloat(form.sale_price)
      const regular = field === "regular_price" ? parseFloat(value) : parseFloat(form.regular_price)
      if (sale && regular && regular > 0) {
        const pct = Math.round((1 - sale / regular) * 100)
        setForm(prev => ({ ...prev, [field]: value, discount: String(pct) }))
      }
    }
  }

  const addDeal = async () => {
    if (!form.game_title || !form.sale_price || !form.regular_price) {
      setError("Game title, sale price, and regular price are required.")
      return
    }
    setLoading(true)
    setError("")
    try {
      await apiRequest("/deals/", {
        method: "POST",
        body: JSON.stringify({ ...form, platform }),
      }, token)
      showSuccess("Deal added!")
      setForm({ game_title: "", platform, sale_price: "", regular_price: "", discount: "", url: "", sale_end_date: "" })
      setShowForm(false)
      loadDeals()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const deleteDeal = async (id, title) => {
    if (!confirm(`Delete "${title}"?`)) return
    try {
      await apiRequest(`/deals/${id}`, { method: "DELETE" }, token)
      showSuccess(`Deleted "${title}"`)
      loadDeals()
    } catch (e) {
      setError(e.message)
    }
  }

  const clearPlatform = async () => {
    if (!confirm(`Clear ALL ${platform.toUpperCase()} deals? This cannot be undone.`)) return
    try {
      await apiRequest(`/deals/clear/${platform}`, { method: "DELETE" }, token)
      showSuccess(`Cleared all ${platform.toUpperCase()} deals`)
      loadDeals()
    } catch (e) {
      setError(e.message)
    }
  }

  const showSuccess = (msg) => {
    setSuccess(msg)
    setTimeout(() => setSuccess(""), 3000)
  }

  return (
    <div style={styles.container}>
      <div style={styles.inner}>

        <div style={styles.header}>
          <h1 style={styles.title}>🛠️ Deal Admin</h1>
          <div style={styles.headerRight}>
            <button style={styles.logoutBtn} onClick={onLogout}>Logout</button>
          </div>
        </div>

        {error   && <div style={styles.error}>{error}</div>}
        {success && <div style={styles.successMsg}>{success}</div>}

        {/* Platform Tabs */}
        <div style={styles.tabs}>
          {PLATFORMS.map(p => (
            <button
              key={p.key}
              style={{ ...styles.tab, ...(platform === p.key ? styles.tabActive : {}) }}
              onClick={() => { setPlatform(p.key); setForm(prev => ({ ...prev, platform: p.key })) }}
            >
              {p.label} ({deals.filter(d => d.platform === p.key).length || (platform === p.key ? deals.length : 0)})
            </button>
          ))}
        </div>

        {/* Actions */}
        <div style={styles.actions}>
          <button style={styles.addBtn} onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ Add Deal"}
          </button>
          <button style={styles.clearBtn} onClick={clearPlatform}>
            Clear All {platform.toUpperCase()} Deals
          </button>
        </div>

        {/* Add Deal Form */}
        {showForm && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Add New Deal</h2>
            <div style={styles.formGrid}>
              <div>
                <label style={styles.label}>Game Title *</label>
                <input style={styles.input} placeholder="e.g. God of War Ragnarök" value={form.game_title} onChange={e => handleFormChange("game_title", e.target.value)} />
              </div>
              <div>
                <label style={styles.label}>Regular Price *</label>
                <input style={styles.input} placeholder="e.g. 59.99" value={form.regular_price} onChange={e => handleFormChange("regular_price", e.target.value)} />
              </div>
              <div>
                <label style={styles.label}>Sale Price *</label>
                <input style={styles.input} placeholder="e.g. 29.99" value={form.sale_price} onChange={e => handleFormChange("sale_price", e.target.value)} />
              </div>
              <div>
                <label style={styles.label}>Discount % (auto-calculated)</label>
                <input style={styles.input} placeholder="e.g. 50" value={form.discount} onChange={e => handleFormChange("discount", e.target.value)} />
              </div>
              <div>
                <label style={styles.label}>Sale End Date</label>
                <input style={styles.input} type="date" value={form.sale_end_date} onChange={e => handleFormChange("sale_end_date", e.target.value)} />
              </div>
              <div>
                <label style={styles.label}>Store URL</label>
                <input style={styles.input} placeholder="https://store.playstation.com/..." value={form.url} onChange={e => handleFormChange("url", e.target.value)} />
              </div>
            </div>
            <button style={styles.saveBtn} onClick={addDeal} disabled={loading}>
              {loading ? "Adding..." : "Add Deal"}
            </button>
          </div>
        )}

        {/* Deals Table */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>
            {platform === "ps" ? "PlayStation" : "Xbox"} Deals ({deals.length})
          </h2>
          {deals.length === 0 ? (
            <p style={styles.empty}>No deals yet — add some above!</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Game</th>
                  <th style={styles.th}>Regular</th>
                  <th style={styles.th}>Sale</th>
                  <th style={styles.th}>Discount</th>
                  <th style={styles.th}>Ends</th>
                  <th style={styles.th}></th>
                </tr>
              </thead>
              <tbody>
                {deals.map(deal => (
                  <tr key={deal.id}>
                    <td style={styles.td}>
                      {deal.url
                        ? <a href={deal.url} target="_blank" rel="noreferrer" style={styles.link}>{deal.game_title}</a>
                        : deal.game_title
                      }
                    </td>
                    <td style={{ ...styles.td, color: "#888", textDecoration: "line-through" }}>{deal.regular_price}</td>
                    <td style={{ ...styles.td, color: "#00c853", fontWeight: "bold" }}>{deal.sale_price}</td>
                    <td style={{ ...styles.td, color: "#ff6b6b", fontWeight: "bold" }}>{deal.discount}% OFF</td>
                    <td style={{ ...styles.td, color: "#aaa", fontSize: "0.85rem" }}>{deal.sale_end_date || "—"}</td>
                    <td style={styles.td}>
                      <button style={styles.deleteBtn} onClick={() => deleteDeal(deal.id, deal.game_title)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  )
}

const styles = {
  container:  { minHeight: "100vh", background: "#1a1a2e", padding: "2rem" },
  inner:      { maxWidth: "900px", margin: "0 auto" },
  header:     { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" },
  title:      { color: "#fff", fontSize: "1.8rem", margin: 0 },
  headerRight:{ display: "flex", gap: "1rem" },
  logoutBtn:  { background: "transparent", border: "1px solid #555", borderRadius: "6px", color: "#aaa", padding: "0.4rem 0.8rem", cursor: "pointer" },
  tabs:       { display: "flex", gap: "0.5rem", marginBottom: "1rem" },
  tab:        { padding: "0.5rem 1.25rem", background: "#0f3460", border: "2px solid #333", borderRadius: "8px", color: "#aaa", cursor: "pointer", fontWeight: "bold" },
  tabActive:  { background: "#0070cc", border: "2px solid #0070cc", color: "#fff" },
  actions:    { display: "flex", gap: "0.75rem", marginBottom: "1rem" },
  addBtn:     { padding: "0.6rem 1.25rem", background: "#0070cc", border: "none", borderRadius: "8px", color: "#fff", fontWeight: "bold", cursor: "pointer" },
  clearBtn:   { padding: "0.6rem 1.25rem", background: "transparent", border: "1px solid #ff4444", borderRadius: "8px", color: "#ff6b6b", cursor: "pointer" },
  card:       { background: "#16213e", borderRadius: "12px", padding: "1.5rem", marginBottom: "1.5rem" },
  cardTitle:  { color: "#fff", marginTop: 0, marginBottom: "1rem" },
  formGrid:   { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" },
  label:      { color: "#aaa", fontSize: "0.85rem", display: "block", marginBottom: "0.4rem" },
  input:      { width: "100%", padding: "0.75rem", background: "#0f3460", border: "1px solid #333", borderRadius: "8px", color: "#fff", fontSize: "1rem", boxSizing: "border-box" },
  saveBtn:    { padding: "0.75rem 1.5rem", background: "#0070cc", border: "none", borderRadius: "8px", color: "#fff", fontWeight: "bold", cursor: "pointer" },
  table:      { width: "100%", borderCollapse: "collapse" },
  th:         { padding: "0.75rem", textAlign: "left", color: "#aaa", fontSize: "0.85rem", borderBottom: "1px solid #0f3460" },
  td:         { padding: "0.75rem", color: "#eee", borderBottom: "1px solid #0f3460" },
  deleteBtn:  { background: "transparent", border: "1px solid #ff4444", borderRadius: "6px", color: "#ff6b6b", padding: "0.3rem 0.6rem", cursor: "pointer", fontSize: "0.85rem" },
  link:       { color: "#0070cc", textDecoration: "none" },
  empty:      { color: "#555", textAlign: "center", padding: "2rem" },
  error:      { background: "#ff000033", border: "1px solid #ff4444", borderRadius: "8px", padding: "0.75rem", color: "#ff6b6b", marginBottom: "1rem" },
  successMsg: { background: "#00c85333", border: "1px solid #00c853", borderRadius: "8px", padding: "0.75rem", color: "#00c853", marginBottom: "1rem" },
}