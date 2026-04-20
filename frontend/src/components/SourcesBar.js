import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import "./SourcesBar.css";

function SourcesBar({ topSources }) {
  if (!topSources || topSources.length === 0) {
    return (
      <div className="sources-container">
        <h3 className="sources-title">Top News Sources</h3>
        <div className="no-data-message">No data yet</div>
      </div>
    );
  }

  return (
    <div className="sources-container">
      <h3 className="sources-title">Top News Sources</h3>
      <BarChart width={400} height={200} data={topSources} layout="vertical">
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={100} />
        <Tooltip />
        <Bar dataKey="count" fill="#378ADD" />
      </BarChart>
    </div>
  );
}

export default SourcesBar;
