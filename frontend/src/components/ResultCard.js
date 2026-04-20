import React, { useState, useEffect } from "react";
import "./ResultCard.css";

function ResultCard({ result }) {
  const [displayConfidence, setDisplayConfidence] = useState(0);
  
  const {
    verdict,
    confidence,
    explanation,
    keyFindings = [],
    trustedSources = [],
    totalSources = 0,
    query = "",
  } = result || {};

  // Animate confidence bar on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayConfidence(confidence);
    }, 100);

    return () => clearTimeout(timer);
  }, [confidence]);
  
  // Return null if result is undefined
  if (!result) {
    return null;
  }

  // Get verdict colors and labels
  const getVerdictStyle = () => {
    if (verdict === "REAL") {
      return {
        bannerBg: "#EAF3DE",
        bannerText: "#27500A",
        bannerBorder: "#639922",
        barColor: "#639922",
        icon: "✓",
        label: "Verified Real",
      };
    } else if (verdict === "FAKE") {
      return {
        bannerBg: "#FCEBEB",
        bannerText: "#791F1F",
        bannerBorder: "#E24B4A",
        barColor: "#E24B4A",
        icon: "✗",
        label: "Likely Fake",
      };
    } else {
      return {
        bannerBg: "#FAEEDA",
        bannerText: "#633806",
        bannerBorder: "#BA7517",
        barColor: "#BA7517",
        icon: "?",
        label: "Cannot Be Verified",
      };
    }
  };

  const getFindingDotColor = () => {
    if (verdict === "REAL") return "#639922";
    if (verdict === "FAKE") return "#E24B4A";
    return "#BA7517";
  };

  const style = getVerdictStyle();

  // Truncate query
  const displayQuery = query.length > 100 ? query.substring(0, 100) + "..." : query;

  // Extract domain from link
  const getDomain = (url) => {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  };

  return (
    <div className="result-card">
      {/* Verdict Banner */}
      <div
        className="verdict-banner"
        style={{
          backgroundColor: style.bannerBg,
          color: style.bannerText,
          borderLeftColor: style.bannerBorder,
        }}
      >
        <div
          className="verdict-icon"
          style={{ backgroundColor: `${style.bannerBorder}20` }}
        >
          {style.icon}
        </div>
        <div>
          <div className="verdict-label">{style.label}</div>
          <div className="verdict-sub">Confidence score: {confidence}%</div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="conf-row">
        <span>Verification confidence</span>
        <span>{displayConfidence}%</span>
      </div>
      <div className="conf-bar-bg">
        <div
          className="conf-bar-fill"
          style={{
            width: `${displayConfidence}%`,
            backgroundColor: style.barColor,
          }}
        />
      </div>

      {/* Explanation Box */}
      <div className="explanation-box">
        <div className="explanation-label">Analysis</div>
        <p className="explanation-text">{explanation}</p>
      </div>

      {/* Key Findings */}
      <div className="findings-section">
        <div className="findings-title">Key Findings</div>
        {Array.isArray(keyFindings) && keyFindings.map((finding, idx) => (
          <div key={idx} className="finding-row">
            <div
              className="finding-dot"
              style={{ backgroundColor: getFindingDotColor() }}
            />
            <span>{finding}</span>
          </div>
        ))}
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-box">
          <div className="stat-number">{trustedSources.length}</div>
          <div className="stat-label">Trusted outlets found</div>
        </div>
        <div className="stat-box">
          <div className="stat-number">{totalSources}</div>
          <div className="stat-label">Total sources checked</div>
        </div>
        <div className="stat-box">
          <div className="stat-number">{confidence}%</div>
          <div className="stat-label">Confidence score</div>
        </div>
      </div>

      {/* Trusted Sources Mini-List */}
      {trustedSources && trustedSources.length > 0 && (
        <div className="trusted-mini">
          <div className="trusted-mini-title">Confirmed by trusted outlets</div>
          {trustedSources.map((source, idx) => (
            <div key={idx} className="trusted-row">
              <img
                src={`https://www.google.com/s2/favicons?domain=${getDomain(
                  source.link
                )}`}
                alt="favicon"
                width="16"
                height="16"
                style={{ borderRadius: "2px" }}
              />
              <a
                href={source.link}
                target="_blank"
                rel="noopener noreferrer"
                className="trusted-link"
              >
                {source.title}
              </a>
            </div>
          ))}
        </div>
      )}

      {/* Search Query Box */}
      <div className="query-box">
        <div className="query-label">Search query used for verification:</div>
        <div className="query-text">{displayQuery}</div>
      </div>
    </div>
  );
}

export default ResultCard;
