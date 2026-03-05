import { useState, useEffect } from "react"
import Login from "./pages/login"
import Signup from "./pages/signup"
import Dashboard from "./pages/dashboard"



export default function App()
{
    const [page,setPage]=useState("login");
    const [token,setToken]=useState(localStorage.getItem("token"));

    useEffect(()=>
    {
        if(token)
        {
            setPage("dashboard");
        }
    },[token])

    const handleLogin=(newToken)=>
    {
        localStorage.setItem("token",newToken);
        setToken(newToken);
        setPage("dashboard");
    }
    const handleLogout=()=>
    {   
        localStorage.removeItem("token");
        setToken(null);
        setPage("login");
    }

    if (page === "dashboard" && token) 
    {
        return <Dashboard token={token} onLogout={handleLogout} />
    }
    if (page === "signup") 
    {
        return <Signup onSignup={handleLogin} onBack={() => setPage("login")} />
    }
    
    return <Login onLogin={handleLogin} onSignup={() => setPage("signup")} />
}