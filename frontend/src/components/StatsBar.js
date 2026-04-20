import React from "react";
import "./StatsBar.css";

function StatsBar({ stats }) {
  return (
    <div className="stats-bar">
      <div className="stat-card">
        <div className="stat-label">Total</div>
        <div className="stat-value">{stats.total}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Fake</div>
        <div className="stat-value fake">{stats.fake}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Real</div>
        <div className="stat-value real">{stats.real}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Fake %</div>
        <div className="stat-value fake">{stats.fakePct}%</div>
      </div>
    </div>
  );
}

export default StatsBar;
