import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getAnalysis } from "../api";
import ScoreGauge from "../components/ScoreGauge";

export default function AnalysisDetail() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    getAnalysis(id).then((res) => setAnalysis(res.data));
  }, [id]);

  if (!analysis) return <p>Loading...</p>;

  return (
    <div>
      <h2>Job-Fit Analysis</h2>
      <ScoreGauge label="Overall Fit Score" score={analysis.fit_score} />
      <ScoreGauge label="Skills Match (50%)" score={analysis.skills_score} />
      <ScoreGauge label="Experience Match (30%)" score={analysis.experience_score} />
      <ScoreGauge label="Education Match (20%)" score={analysis.education_score} />

      <h3>Matching Skills</h3>
      <p>{(analysis.matching_skills || []).join(", ") || "None"}</p>

      <h3>Missing Skills</h3>
      <p>{(analysis.missing_skills || []).join(", ") || "None"}</p>

      <h3>Learning Recommendations</h3>
      <ul>
        {(analysis.recommendations?.learning_plan || []).map((item, idx) => (
          <li key={idx}>
            <strong>{item.skill}</strong>: {item.suggestion} (~{item.estimated_weeks} weeks)
          </li>
        ))}
      </ul>

      <h3>Interview Preparation</h3>
      <h4>Technical Questions</h4>
      <ul>
        {(analysis.interview_prep?.technical_questions || []).map((q, idx) => (
          <li key={idx}>{q}</li>
        ))}
      </ul>
      <h4>Behavioral Questions</h4>
      <ul>
        {(analysis.interview_prep?.behavioral_questions || []).map((q, idx) => (
          <li key={idx}>{q}</li>
        ))}
      </ul>
      <h4>Topics to Revise</h4>
      <p>{(analysis.interview_prep?.topics_to_revise || []).join(", ") || "None"}</p>
    </div>
  );
}
