import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAnalyses } from "../api";

export default function History() {
  const [analyses, setAnalyses] = useState([]);

  useEffect(() => {
    listAnalyses().then((res) => setAnalyses(res.data));
  }, []);

  return (
    <div>
      <h2>Analysis History</h2>
      {analyses.length === 0 && <p>No past analyses yet.</p>}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Date</th>
            <th>Fit Score</th>
            <th>Skills</th>
            <th>Experience</th>
            <th>Education</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {analyses.map((a) => (
            <tr key={a.id}>
              <td>{new Date(a.created_at).toLocaleString()}</td>
              <td>{a.fit_score}%</td>
              <td>{a.skills_score}%</td>
              <td>{a.experience_score}%</td>
              <td>{a.education_score}%</td>
              <td>
                <Link to={`/analysis/${a.id}`}>View</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
