const mongoose = require("mongoose");

const articleSchema = new mongoose.Schema({
  id: {
    type: String,
    unique: true,
    required: true,
  },
  title: String,
  description: String,
  source: String,
  url: String,
  publishedAt: String,
  label: {
    type: String,
    enum: ["FAKE", "REAL", "UNKNOWN"],
    default: "UNKNOWN",
  },
  confidence: Number,
  receivedAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model("Article", articleSchema);
