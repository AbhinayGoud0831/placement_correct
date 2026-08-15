import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadResume } from "../api";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError("");
    setLoading(true);
    try {
      await uploadResume(file);
      navigate("/analyze");
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload Resume</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Processing (parsing + AI extraction)..." : "Upload & Analyze"}
        </button>
      </form>
      <p style={{ color: "#666" }}>Accepted formats: PDF, DOCX.</p>
    </div>
  );
}
