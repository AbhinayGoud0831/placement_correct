import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const isAuthed = !!localStorage.getItem("access_token");

  const logout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <nav>
      <Link to="/" style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
        📊 Placement Intelligence
      </Link>
      {isAuthed && (
        <>
          <Link to="/">Dashboard</Link>
          <Link to="/discover">Discover Jobs</Link>
          <Link to="/upload-resume">Upload Resume</Link>
          <Link to="/analyze">Analyze</Link>
          <Link to="/history">History</Link>
        </>
      )}
      <div>
        {isAuthed ? (
          <button onClick={logout} style={{ marginLeft: "1rem" }}>
            Logout
          </button>
        ) : (
          <>
            <Link to="/login" style={{ marginRight: "1rem" }}>
              Login
            </Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
