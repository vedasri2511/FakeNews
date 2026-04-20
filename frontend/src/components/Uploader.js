import React, { useState, useRef } from "react";
import "./Uploader.css";

function Uploader({ onFileSelect, loading }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const fileInputRef = useRef(null);

  const acceptedExtensions = [".pdf", ".docx", ".txt", ".csv", ".jpg", ".jpeg", ".png"];

  // Helper function to format file size
  function formatSize(bytes) {
    if (bytes < 1024 * 1024) {
      return (bytes / 1024).toFixed(1) + " KB";
    } else {
      return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }
  }

  // Handle file validation and selection
  function handleFile(file) {
    if (!file) return;

    const fileName = file.name.toLowerCase();
    const ext = fileName.substring(fileName.lastIndexOf("."));

    if (!acceptedExtensions.includes(ext)) {
      setFileError("Unsupported format. Accepted: PDF, DOCX, TXT, CSV, JPG, PNG");
      setSelectedFile(null);
    } else {
      setSelectedFile(file);
      setFileError(null);
    }
  }

  // Handle drag over
  function handleDragOver(e) {
    e.preventDefault();
    setDragOver(true);
  }

  // Handle drag leave
  function handleDragLeave() {
    setDragOver(false);
  }

  // Handle drop
  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }

  // Handle file input change
  function handleChange(e) {
    const file = e.target.files[0];
    handleFile(file);
  }

  // Handle submit
  function handleSubmit() {
    if (!selectedFile) {
      setFileError("Please select a file to verify");
      return;
    }
    onFileSelect(selectedFile);
  }

  // Handle remove file
  function handleRemove() {
    setSelectedFile(null);
    setFileError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <div className="uploader">
      {/* Drop Zone */}
      <div
        className={`drop-zone ${dragOver ? "active" : ""}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon">↑</div>
        <h3>Drag & drop your file here</h3>
        <p>or click to browse</p>
        <div className="formats-row">
          PDF · DOCX · TXT · CSV · JPG · PNG · up to 20MB
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.csv,.jpg,.jpeg,.png"
          onChange={handleChange}
          style={{ display: "none" }}
        />
      </div>

      {/* Selected File Info */}
      {selectedFile && (
        <div className="file-info">
          <div>
            <div className="file-name">{selectedFile.name}</div>
            <div className="file-size">{formatSize(selectedFile.size)}</div>
          </div>
          <button className="remove-btn" onClick={handleRemove}>
            ×
          </button>
        </div>
      )}

      {/* Error Message */}
      {fileError && <div className="file-error">{fileError}</div>}

      {/* Submit Button */}
      <button
        className="submit-btn"
        onClick={handleSubmit}
        disabled={loading || !selectedFile}
      >
        {loading ? "Verifying..." : "Verify Article"}
      </button>
    </div>
  );
}

export default Uploader;
