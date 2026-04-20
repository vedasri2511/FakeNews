import React from "react";
import { PieChart, Pie, Legend, Cell } from "recharts";
import "./DonutChart.css";

function DonutChart({ stats }) {
  let data = [
    { name: "Fake", value: stats.fake, fill: "#E24B4A" },
    { name: "Real", value: stats.real, fill: "#639922" },
  ];

  // If both are 0, show placeholder
  if (stats.fake === 0 && stats.real === 0) {
    data = [{ name: "No data", value: 1, fill: "#cccccc" }];
  }

  return (
    <div className="donut-chart-container">
      <PieChart width={300} height={220}>
        <Pie
          data={data}
          dataKey="value"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={3}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Pie>
        <Legend />
      </PieChart>
    </div>
  );
}

export default DonutChart;
