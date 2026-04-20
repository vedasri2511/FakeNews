import React from "react";
import "./ArticleFeed.css";

function ArticleFeed({ articles, filter }) {
  // Filter articles based on the filter prop
  const filteredArticles = articles.filter((article) => {
    if (filter === "ALL") return true;
    if (filter === "FAKE") return article.label === "FAKE";
    if (filter === "REAL") return article.label === "REAL";
    return true;
  });

  // Show max 20 articles
  const displayedArticles = filteredArticles.slice(0, 20);

  return (
    <div className="article-feed">
      <h3 className="feed-title">Recent Articles</h3>
      {displayedArticles.length === 0 ? (
        <div className="no-articles">No articles yet</div>
      ) : (
        <div className="articles-list">
          {displayedArticles.map((article, index) => (
            <div key={article.id || index} className="article-card">
              <div className="article-header">
                <div className="article-title-section">
                  <div className="article-title">{article.title}</div>
                  <div className="article-meta">
                    {article.source} · {article.confidence}%
                  </div>
                </div>
                <div
                  className={`article-badge badge-${article.label.toLowerCase()}`}
                >
                  {article.label}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ArticleFeed;
