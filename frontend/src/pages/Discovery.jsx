import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Discovery() {
  const [jobs, setJobs] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("browse");
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    loadJobs();
    loadResumes();
  }, []);

  const loadJobs = (searchTerm = "") => {
    api
      .get("/api/discovery", { params: { search: searchTerm } })
      .then((res) => setJobs(res.data))
      .catch(() => {
        setJobs([]);
      });
  };

  const loadResumes = () => {
    api
      .get("/api/resumes")
      .then((res) => {
        setResumes(res.data);
        if (res.data.length) setSelectedResume(res.data[0].id);
      })
      .catch(() => {});
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setRefreshMessage("");
    try {
      const res = await api.post("/api/discovery/refresh", null, { params: { limit: 50 } });
      setRefreshMessage(`${res.data.added_or_updated} live job(s) added/updated.` + (res.data.warnings?.length ? " Some sources were unavailable; cached/demo jobs remain available." : ""));
      loadJobs(search);
    } catch (err) {
      setRefreshMessage(err.response?.data?.detail || "Live refresh failed. Cached jobs are still available.");
    } finally {
      setRefreshing(false);
    }
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    loadJobs(e.target.value);
  };

  const handleGetRecommendations = async () => {
    if (!selectedResume) {
      alert("Please upload a resume first");
      return;
    }
    setLoading(true);
    try {
      const res = await api.get("/api/discovery/recommend", {
        params: { resume_id: selectedResume, top_k: 10 },
      });
      setRecommendations(res.data);
      setActiveTab("recommendations");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to get recommendations");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeJob = async (job) => {
    // Create/save this job to database if it's from sample_jobs (not from manual entry)
    // Then navigate to analysis with both resume_id and job_id
    try {
      // If job.id exists, it's from sample_jobs; otherwise create a new JD entry
      if (job.id && job.id.length === 36) {
        // UUID format - it's from sample_jobs
        navigate("/analyze", {
          state: { preset_job_id: job.id, preset_job_title: job.title, preset_resume_id: selectedResume },
        });
      } else {
        // Fallback: navigate to analyze page where user can paste JD manually
        navigate("/analyze");
      }
    } catch (err) {
      alert("Error navigating to analysis");
    }
  };

  return (
    <div>
      <h2>🔍 Job Discovery & Recommendations</h2>

      <div style={{ marginBottom: "2rem" }}>
        <button onClick={handleRefresh} disabled={refreshing} style={{ marginBottom: "1rem" }}>
          {refreshing ? "Refreshing live jobs..." : "↻ Refresh Live Jobs"}
        </button>
        {refreshMessage && <p style={{ fontSize: "0.9rem", color: "#555" }}>{refreshMessage}</p>}
        <button
          onClick={() => setActiveTab("browse")}
          style={{
            marginRight: "1rem",
            background: activeTab === "browse" ? "#3498db" : "#bdc3c7",
          }}
        >
          📋 Browse Jobs
        </button>
        <button
          onClick={() => setActiveTab("recommendations")}
          style={{
            background: activeTab === "recommendations" ? "#3498db" : "#bdc3c7",
          }}
        >
          ⭐ AI Recommendations
        </button>
      </div>

      {activeTab === "browse" && (
        <div>
          <div style={{ marginBottom: "1.5rem", background: "white", padding: "1.5rem", borderRadius: "8px" }}>
            <label>Search Jobs by Title or Company</label>
            <input
              type="text"
              placeholder="E.g., Python, Backend, Senior..."
              value={search}
              onChange={handleSearch}
            />
            <p style={{ marginTop: "0.5rem", fontSize: "0.9rem", color: "#7f8c8d" }}>
              {jobs.length} job(s) found
            </p>
          </div>

          <div>
            {jobs.length === 0 && <p>No jobs found. Try a different search term.</p>}
            {jobs.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <div>
                    <div className="job-title">{job.title}</div>
                    <div className="job-company">{job.company}</div>
                  </div>
                  {job.level && <span className="job-level">{job.level}</span>}
                </div>
                <p>{job.description.substring(0, 200)}...</p>
                <p style={{ fontSize: "0.82rem", color: "#7f8c8d" }}>{job.source || "Demo"} · {job.location || "Location not specified"}</p>
                {job.url && <a href={job.url} target="_blank" rel="noreferrer">View original listing ↗</a>}
                <button
                  onClick={() => handleAnalyzeJob(job)}
                  style={{ marginTop: "0.5rem" }}
                >
                  Analyze My Match
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "recommendations" && (
        <div>
          <div style={{ marginBottom: "1.5rem", background: "white", padding: "1.5rem", borderRadius: "8px" }}>
            <label>Select Resume for Personalized Recommendations</label>
            {resumes.length === 0 ? (
              <p>Please upload a resume first.</p>
            ) : (
              <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                <select value={selectedResume} onChange={(e) => setSelectedResume(e.target.value)}>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.original_filename}
                    </option>
                  ))}
                </select>
                <button onClick={handleGetRecommendations} disabled={loading}>
                  {loading ? "Analyzing..." : "Get Recommendations"}
                </button>
              </div>
            )}
          </div>

          {recommendations.length === 0 && <p>No recommendations yet.</p>}
          {recommendations.map((rec) => (
            <div key={rec.job_id} className="job-card">
              <div className="job-header">
                <div>
                  <div className="job-title">{rec.title}</div>
                  <div className="job-company">{rec.company}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="fit-score">{rec.fit_score}% Match</div>
                  <div style={{ fontSize: "0.85rem", color: "#7f8c8d" }}>
                    {rec.level && `(${rec.level})`}
                  </div>
                </div>
              </div>
              <p style={{ fontSize: "0.95rem", marginBottom: "1rem" }}>{rec.reason}</p>
              <button onClick={() => handleAnalyzeJob(rec)}>View Full Analysis</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
