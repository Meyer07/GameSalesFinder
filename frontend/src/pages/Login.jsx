import React,{useState} from "react"
import {apiRequest} from "../api"

export default function Login({onLogin , onSignup})
{
    const [email,setEmail]= useState("");
    const [password,setPassword]=useState("");
    const [error,setError]=useState("");
    const [loading,isLoading]=useState(false);


    const handleSubmit =async ()=>
    {
        setError("");
        isLoading(true);

        try
        {
            const data = await apiRequest("/auth/login",
                {
                    method:"POST",
                    body:JSON.stringify({email,password})
                });
            onLogin(data.access_token);
        }catch(e)
        {
            setError(e.message);
        }finally
        {
            isLoading(false);
        }
    }


    return (
        <div style={styles.container}>
          <div style={styles.card}>
            <h1 style={styles.title}>🎮 Game Deals Finder</h1>
            <p style={styles.subtitle}>Sign in to manage your wishlist</p>
    
            {error && <div style={styles.error}>{error}</div>}
    
            <input
              style={styles.input}
              type="email"
              placeholder="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
            <input
              style={styles.input}
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
            />
    
            <button style={styles.button} onClick={handleSubmit} disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>
    
            <p style={styles.link}>
              Don't have an account?{" "}
              <span style={styles.linkText} onClick={onSignup}>Sign up</span>
            </p>
          </div>
        </div>
      )
    }
    
    const styles = {
      container: { minHeight: "100vh", background: "#1a1a2e", display: "flex", alignItems: "center", justifyContent: "center" },
      card:      { background: "#16213e", padding: "2.5rem", borderRadius: "12px", width: "100%", maxWidth: "400px", boxShadow: "0 8px 32px rgba(0,0,0,0.4)" },
      title:     { color: "#fff", fontSize: "2rem", marginBottom: "0.25rem", textAlign: "center" },
      subtitle:  { color: "#aaa", textAlign: "center", marginBottom: "1.5rem" },
      input:     { width: "100%", padding: "0.75rem", marginBottom: "1rem", background: "#0f3460", border: "1px solid #333", borderRadius: "8px", color: "#fff", fontSize: "1rem", boxSizing: "border-box" },
      button:    { width: "100%", padding: "0.75rem", background: "#0070cc", border: "none", borderRadius: "8px", color: "#fff", fontSize: "1rem", cursor: "pointer", fontWeight: "bold" },
      error:     { background: "#ff000033", border: "1px solid #ff4444", borderRadius: "8px", padding: "0.75rem", color: "#ff6b6b", marginBottom: "1rem" },
      link:      { color: "#aaa", textAlign: "center", marginTop: "1rem" },
      linkText:  { color: "#0070cc", cursor: "pointer", fontWeight: "bold" },
}
