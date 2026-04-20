import React from "react";
import "./FilterButtons.css";

function FilterButtons({ filter, setFilter }) {
  return (
    <div className="filter-buttons">
      <button
        className={`filter-btn ${filter === "ALL" ? "active-all" : ""}`}
        onClick={() => setFilter("ALL")}
      >
        All
      </button>
      <button
        className={`filter-btn ${filter === "FAKE" ? "active-fake" : ""}`}
        onClick={() => setFilter("FAKE")}
      >
        Fake only
      </button>
      <button
        className={`filter-btn ${filter === "REAL" ? "active-real" : ""}`}
        onClick={() => setFilter("REAL")}
      >
        Real only
      </button>
    </div>
  );
}

export default FilterButtons;
