import React from "react";
import { Outlet, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Layout.css";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="topbar-logo">
            <span className="logo-icon">💊</span>
            <span className="logo-text">MediLembre</span>
          </Link>
          <div className="topbar-right">
            <span className="topbar-user">Olá, {user?.name?.split(" ")[0]}</span>
            <button className="btn-ghost btn-sm" onClick={handleLogout}>Sair</button>
          </div>
        </div>
      </header>
      <main className="main-content">
        <div className="main-inner">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
