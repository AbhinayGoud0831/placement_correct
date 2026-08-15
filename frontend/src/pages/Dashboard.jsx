import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMe, listAnalyses, listResumes } from "../api";

export default function Dashboard() {
  const [student, setStudent] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    getMe().then((res) => setStudent(res.data)).catch(() => {});
    listAnalyses().then((res) => setAnalyses(res.data)).catch(() => {});
    listResumes().then((res) => setResumes(res.data)).catch(() => {});
  }, []);

  return (
    <div>
      <h2>Welcome{student ? `, ${student.full_name}` : ""}</h2>
      <div style={{ display: "flex", gap: "2rem", margin: "1.5rem 0" }}>
        <div>
          <h3>{resumes.length}</h3>
          <p>Resumes uploaded</p>
        </div>
        <div>
          <h3>{analyses.length}</h3>
          <p>Analyses run</p>
        </div>
        <div>
          <h3>
            {analyses.length
              ? Math.round(analyses.reduce((s, a) => s + a.fit_score, 0) / analyses.length)
              : 0}
            %
          </h3>
          <p>Average fit score</p>
        </div>
      </div>

      <p>
        <Link to="/upload-resume">Upload a new resume</Link> &nbsp;|&nbsp;
        <Link to="/analyze"> Analyze against a job description</Link>
      </p>

      <h3>Recent Analyses</h3>
      {analyses.length === 0 && <p>No analyses yet.</p>}
      <ul>
        {analyses.slice(0, 5).map((a) => (
          <li key={a.id}>
            <Link to={`/analysis/${a.id}`}>
              Fit Score: {a.fit_score}% — {new Date(a.created_at).toLocaleString()}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
