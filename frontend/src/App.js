import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import Uploader from "./components/Uploader";
import ResultCard from "./components/ResultCard";
import SourcesList from "./components/SourcesList";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inputText, setInputText] = useState("");
  const [inputTitle, setInputTitle] = useState("");
  const [activeTab, setActiveTab] = useState("upload");

  // Handle verification
  async function handleVerify(formData) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post("http://localhost:5000/api/verify", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Verification failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Handle file submission
  function handleFileSubmit(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", inputTitle);
    handleVerify(formData);
  }

  // Handle text submission
  function handleTextSubmit() {
    if (inputText.trim() === "") {
      setError("Please enter article text");
      return;
    }

    const formData = new FormData();
    formData.append("text", inputText);
    formData.append("title", inputTitle);
    handleVerify(formData);
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-icon">⚡</div>
        <h1>Fake News Detector</h1>
        <p>Upload or paste any article — instantly verified against 20+ trusted global news sources</p>
      </header>

      {/* Tab Bar */}
      <div className="tab-bar">
        <button
          className={`tab-button ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          Upload File
        </button>
        <button
          className={`tab-button ${activeTab === "text" ? "active" : ""}`}
          onClick={() => setActiveTab("text")}
        >
          Paste Text
        </button>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Title Input */}
        <div className="form-section">
          <input
            type="text"
            placeholder="Article headline or title (optional — improves accuracy)"
            value={inputTitle}
            onChange={(e) => setInputTitle(e.target.value)}
            className="title-input"
            disabled={loading}
          />

          {/* Upload Tab */}
          {activeTab === "upload" && (
            <Uploader onFileSelect={handleFileSubmit} loading={loading} />
          )}

          {/* Text Tab */}
          {activeTab === "text" && (
            <div className="text-input-section">
              <textarea
                rows="8"
                placeholder="Paste your full news article or claim here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="article-textarea"
                disabled={loading}
              />
              <button
                className="verify-button"
                onClick={handleTextSubmit}
                disabled={loading}
              >
                {loading ? "Verifying..." : "Verify Article"}
              </button>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p className="loading-text">Searching across 20+ trusted news sources worldwide...</p>
            <p className="loading-subtext">This may take a few seconds</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-box">
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="results-section">
            <ResultCard result={result} />
            <SourcesList sources={result.sources} trusted={result.trustedSources} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
