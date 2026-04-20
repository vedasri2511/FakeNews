import React, { useState } from "react";
import "./SourcesList.css";

function SourcesList({ sources = [], trusted = [] }) {
  const [showAll, setShowAll] = useState(false);
  const [filter, setFilter] = useState("all");

  const trustedDomains = [
    "bbc.com",
    "reuters.com",
    "apnews.com",
    "nytimes.com",
    "theguardian.com",
    "ndtv.com",
    "thehindu.com",
    "hindustantimes.com",
    "washingtonpost.com",
    "cnn.com",
    "aljazeera.com",
    "bloomberg.com",
    "forbes.com",
    "economist.com",
    "npr.org",
    "abcnews.go.com",
    "cbsnews.com",
    "nbcnews.com",
    "time.com",
    "usatoday.com",
    "bbc.co.uk",
    "indiatoday.in",
    "timesofindia.com",
    "theprint.in",
  ];

  // Helper to check if link is trusted
  function isTrusted(link) {
    return trustedDomains.some((domain) => link.includes(domain));
  }

  // Helper to extract domain
  function getDomain(link) {
    try {
      return new URL(link).hostname;
    } catch {
      return link;
    }
  }

  // Determine displayed sources
  let displayed = filter === "trusted" ? trusted : sources;
  if (!displayed) {
    displayed = [];
  }
  if (!showAll) {
    displayed = displayed.slice(0, 4);
  }

  // Empty state
  if (!sources || sources.length === 0) {
    return (
      <div className="sources-section">
        <div className="sources-header">
          <h2 className="sources-title">Sources Checked</h2>
        </div>
        <div className="empty-state">No sources were found for this article.</div>
      </div>
    );
  }

  const totalToShow = filter === "all" ? sources : trusted;

  return (
    <div className="sources-section">
      {/* Section Header */}
      <div className="sources-header">
        <h2 className="sources-title">Sources Checked</h2>
        <span className="results-badge">{sources.length} results</span>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        <button
          className={`filter-tab ${filter === "all" ? "active" : ""}`}
          onClick={() => {
            setFilter("all");
            setShowAll(false);
          }}
        >
          All Sources ({sources.length})
        </button>
        <button
          className={`filter-tab ${filter === "trusted" ? "active" : ""}`}
          onClick={() => {
            setFilter("trusted");
            setShowAll(false);
          }}
        >
          Trusted Only ({trusted.length})
        </button>
      </div>

      {/* Info Strip */}
      <div className="info-strip">
        We searched Google across 20+ trusted outlets. Trusted sources (marked in
        green) are major verified news organizations. More trusted matches =
        higher confidence.
      </div>

      {/* Source Cards */}
      {displayed.length > 0 ? (
        <div>
          {displayed.map((source, idx) => {
            const trusted_check = isTrusted(source.link);
            const domain = getDomain(source.link);
            const snippetTrunc =
              source.snippet && source.snippet.length > 180
                ? source.snippet.substring(0, 180) + "..."
                : source.snippet;

            return (
              <div
                key={idx}
                className={`source-card ${trusted_check ? "trusted" : "normal"}`}
              >
                {/* Card Top */}
                <div className="card-top">
                  <img
                    src={`https://www.google.com/s2/favicons?domain=${domain}`}
                    alt="favicon"
                    width="16"
                    height="16"
                    style={{ borderRadius: "2px" }}
                  />
                  <span className="source-domain">{domain}</span>
                  {trusted_check && (
                    <span className="trusted-pill">Trusted</span>
                  )}
                </div>

                {/* Title */}
                <div className="source-title">
                  <a href={source.link} target="_blank" rel="noopener noreferrer">
                    {source.title}
                  </a>
                </div>

                {/* Snippet */}
                <div className="source-snippet">{snippetTrunc}</div>

                {/* Card Bottom */}
                <div className="card-bottom">
                  <span className="domain-pill">{domain}</span>
                  <a href={source.link} target="_blank" rel="noopener noreferrer" className="open-link">
                    Open source →
                  </a>
                </div>
              </div>
            );
          })}

          {/* Show More Button */}
          {totalToShow.length > 4 && (
            <button
              className="show-more-btn"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll
                ? "Show fewer ↑"
                : `Show all ${totalToShow.length} sources ↓`}
            </button>
          )}
        </div>
      ) : (
        <div className="empty-state">No sources were found for this article.</div>
      )}
    </div>
  );
}

export default SourcesList;
