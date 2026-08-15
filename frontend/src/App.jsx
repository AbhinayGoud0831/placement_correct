import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import UploadResume from "./pages/UploadResume";
import JobAnalysis from "./pages/JobAnalysis";
import AnalysisDetail from "./pages/AnalysisDetail";
import History from "./pages/History";
import Discovery from "./pages/Discovery";

function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

function PrivateRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/discover"
            element={
              <PrivateRoute>
                <Discovery />
              </PrivateRoute>
            }
          />
          <Route
            path="/upload-resume"
            element={
              <PrivateRoute>
                <UploadResume />
              </PrivateRoute>
            }
          />
          <Route
            path="/analyze"
            element={
              <PrivateRoute>
                <JobAnalysis />
              </PrivateRoute>
            }
          />
          <Route
            path="/analysis/:id"
            element={
              <PrivateRoute>
                <AnalysisDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/history"
            element={
              <PrivateRoute>
                <History />
              </PrivateRoute>
            }
          />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
