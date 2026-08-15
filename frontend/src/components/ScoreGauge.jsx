import React from "react";

export default function ScoreGauge({ label, score }) {
  const color = score >= 75 ? "#2e7d32" : score >= 50 ? "#f9a825" : "#c62828";
  return (
    <div style={{ marginBottom: "0.75rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span>{label}</span>
        <strong>{score}%</strong>
      </div>
      <div style={{ background: "#eee", borderRadius: 4, height: 10 }}>
        <div
          style={{
            width: `${Math.min(100, Math.max(0, score))}%`,
            background: color,
            height: "100%",
            borderRadius: 4,
          }}
        />
      </div>
    </div>
  );
}
