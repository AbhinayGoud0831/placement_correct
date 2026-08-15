import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { createJob, listResumes, runAnalysis } from "../api";

export default function JobAnalysis() {
  const [resumes, setResumes] = useState([]);
  const [resumeId, setResumeId] = useState("");
  const [title, setTitle] = useState("");
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [presetJobId, setPresetJobId] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    listResumes().then((res) => {
      setResumes(res.data);
      if (res.data.length) setResumeId(res.data[0].id);
    });

    // Check if we came from Discovery with a preset job
    if (location.state?.preset_job_id) {
      setPresetJobId(location.state.preset_job_id);
      setTitle(location.state.preset_job_title || "");
      if (location.state.preset_resume_id) setResumeId(location.state.preset_resume_id);
    }
  }, [location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // If using preset job from sample_jobs, use that directly
    if (presetJobId) {
      setLoading(true);
      try {
        const analysisRes = await runAnalysis(resumeId, presetJobId);
        navigate(`/analysis/${analysisRes.data.id}`);
      } catch (err) {
        setError(err.response?.data?.detail || "Analysis failed");
      } finally {
        setLoading(false);
      }
      return;
    }

    // Otherwise, create a new job description entry
    if (jdText.trim().length < 50) {
      setError("Job description must be at least 50 characters");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const jobRes = await createJob({ title: title.trim() || "Custom Job", raw_text: jdText.trim() });
      const analysisRes = await runAnalysis(resumeId, jobRes.data.id);
      navigate(`/analysis/${analysisRes.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const isValid = resumeId && (presetJobId || jdText.trim().length >= 50);

  return (
    <div>
      <h2>Analyze Resume Against a Job</h2>
      {resumes.length === 0 ? (
        <p>Upload a resume first.</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Select Resume</label>
            <select value={resumeId} onChange={(e) => setResumeId(e.target.value)}>
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.original_filename}
                </option>
              ))}
            </select>
          </div>

          {presetJobId ? (
            <div style={{ background: "#d4edda", padding: "1rem", borderRadius: "4px", marginBottom: "1.5rem" }}>
              <p style={{ color: "#155724", marginBottom: "0.5rem" }}>
                ✓ <strong>Using job from Discovery:</strong> {title}
              </p>
              <button
                type="button"
                onClick={() => {
                  setPresetJobId(null);
                  setTitle("");
                  setJdText("");
                }}
                style={{ background: "#155724", fontSize: "0.85rem" }}
              >
                Use a different job
              </button>
            </div>
          ) : (
            <div>
              <label>Job Title (optional)</label>
              <input value={title} onChange={(e) => setTitle(e.target.value)} />

              <label style={{ marginTop: "1rem" }}>Job Description ({jdText.length} characters)</label>
              <textarea
                rows={10}
                style={{ width: "100%" }}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the full job description here..."
                required={!presetJobId}
              />
              {jdText.length < 50 && jdText.length > 0 && (
                <p style={{ color: "#666", fontSize: "0.9em" }}>
                  Minimum 50 characters required ({50 - jdText.length} more needed)
                </p>
              )}
            </div>
          )}

          {error && <p style={{ color: "red" }}>{error}</p>}

          <button type="submit" disabled={loading || !isValid} style={{ marginTop: "1rem" }}>
            {loading ? "Analyzing..." : "Run Analysis"}
          </button>
        </form>
      )}
    </div>
  );
}
