const express = require("express");
const multer = require("multer");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const pdfParse = require("pdf-parse");
const mammoth = require("mammoth");
const { PythonShell } = require("python-shell");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json({ limit: "20mb" }));

// Create uploads folder
const uploadsDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const upload = multer({ dest: "uploads/", limits: { fileSize: 20 * 1024 * 1024 } });

// ──────────────────────────────────────
// TEXT EXTRACTION
// ──────────────────────────────────────
async function extractText(filePath, originalname) {
  try {
    const ext = path.extname(originalname).toLowerCase();

    if (ext === ".pdf") {
      const dataBuffer = fs.readFileSync(filePath);
      const data = await pdfParse(dataBuffer);
      fs.unlinkSync(filePath);
      return data.text;
    } else if (ext === ".docx") {
      const result = await mammoth.extractRawText({ path: filePath });
      fs.unlinkSync(filePath);
      return result.value;
    } else if ([".jpg", ".jpeg", ".png", ".gif"].includes(ext)) {
      fs.unlinkSync(filePath);
      return "IMAGE_UPLOAD";
    } else {
      const text = fs.readFileSync(filePath, "utf-8");
      fs.unlinkSync(filePath);
      return text;
    }
  } catch (error) {
    console.error("Text extraction error:", error);
    return "";
  }
}

// ──────────────────────────────────────
// ML MODEL PREDICTION (REAL)
// ──────────────────────────────────────
async function predictWithMLModel(text) {
  try {
    console.log("🤖 Using ML Model for prediction...");
    
    const options = {
      mode: "text",
      pythonPath: process.env.PYTHON_PATH || "python",
      pythonOptions: ["-u"],
      scriptPath: path.join(__dirname, "../ml"),
      args: [text.substring(0, 2000)], // Limit text length
    };

    return new Promise((resolve, reject) => {
      PythonShell.run("predict.py", options, (err, results) => {
        if (err) {
          console.warn("ML Model error:", err);
          resolve(null);
          return;
        }

        try {
          const result = JSON.parse(results[0]);
          console.log(`✓ ML Prediction: ${result.label} (${result.confidence.toFixed(1)}%)`);
          resolve(result);
        } catch (parseErr) {
          console.warn("Failed to parse ML result:", parseErr);
          resolve(null);
        }
      });
    });
  } catch (error) {
    console.warn("ML prediction failed:", error.message);
    return null;
  }
}

// ──────────────────────────────────────
// FETCH REAL NEWS (NewsAPI)
// ──────────────────────────────────────
async function fetchRealNews(query) {
  try {
    const apiKey = process.env.NEWS_API_KEY;
    
    if (!apiKey) {
      console.warn("⚠ NEWS_API_KEY not configured");
      return [];
    }

    console.log(`📰 Fetching real news for: "${query}"`);
    
    const response = await axios.get("https://newsapi.org/v2/everything", {
      params: {
        q: query.substring(0, 100),
        apiKey: apiKey,
        pageSize: 10,
        sortBy: "relevancy",
        language: "en",
      },
      timeout: 5000,
    });

    if (response.data.status === "ok" && response.data.articles) {
      console.log(`✓ Found ${response.data.articles.length} real news articles`);
      return response.data.articles.map((article) => ({
        source: article.source.name,
        title: article.title,
        content: article.description || "",
        url: article.url,
        date: article.publishedAt,
        image: article.urlToImage,
      }));
    }

    return [];
  } catch (error) {
    console.error("NewsAPI error:", error.message);
    return [];
  }
}

// ──────────────────────────────────────
// ANALYZE RESULTS (Real-world scoring)
// ──────────────────────────────────────
async function analyzeArticle(articleText, title, mlPrediction, realNews) {
  console.log("\n" + "=".repeat(60));
  console.log("ANALYZING ARTICLE");
  console.log("=".repeat(60));

  // Score 1: ML Model Prediction (40% weight)
  let mlScore = 50; // Default neutral
  if (mlPrediction) {
    mlScore = mlPrediction.confidence;
    console.log(`\n1️⃣  ML MODEL: ${mlPrediction.label} (${mlScore.toFixed(1)}%)`);
  } else {
    console.log("\n1️⃣  ML MODEL: Not available");
  }

  // Score 2: News Coverage (40% weight)
  const articleWords = articleText.toLowerCase().split(/\s+/).filter((w) => w.length > 3);
  const newsMatches = realNews.filter((news) => {
    const newsWords = `${news.title} ${news.content}`.toLowerCase().split(/\s+/);
    const matches = articleWords.filter((word) => newsWords.includes(word)).length;
    return matches > 5; // At least 5 word matches
  });

  let newsScore = 20; // Base score if no matching news
  if (newsMatches.length > 0) {
    newsScore = Math.min(100, 40 + newsMatches.length * 10);
    console.log(`\n2️⃣  NEWS COVERAGE: ${newsMatches.length} matching article(s) found`);
    console.log(`     Score: ${newsScore.toFixed(1)}%`);
  } else {
    console.log(`\n2️⃣  NEWS COVERAGE: No matching articles found`);
    console.log(`     Score: ${newsScore.toFixed(1)}%`);
  }

  // Score 3: Content Quality (20% weight)
  let contentScore = 50;
  const suspiciousKeywords = [
    "overnight",
    "secret",
    "hidden",
    "shocking",
    "cure all",
    "guaranteed",
    "dont want you to know",
  ];
  const suspiciousCount = suspiciousKeywords.filter((kw) =>
    articleText.toLowerCase().includes(kw)
  ).length;

  if (suspiciousCount > 3) {
    contentScore = 20;
    console.log(`\n3️⃣  CONTENT QUALITY: Suspicious language detected (${suspiciousCount} keywords)`);
    console.log(`     Score: ${contentScore.toFixed(1)}%`);
  } else {
    console.log(`\n3️⃣  CONTENT QUALITY: Standard language (${suspiciousCount} suspicious keywords)`);
    console.log(`     Score: ${contentScore.toFixed(1)}%`);
  }

  // Calculate final score
  const finalScore = (mlScore * 0.4 + newsScore * 0.4 + contentScore * 0.2) / 100 * 100;

  // Determine verdict
  let verdict, explanation;
  if (mlPrediction && mlPrediction.label === "FAKE") {
    verdict = "FAKE";
    explanation = `❌ ML Model classified this as FAKE NEWS with ${mlPrediction.confidence.toFixed(1)}% confidence. No credible news sources are reporting this story.`;
  } else if (newsMatches.length > 0) {
    verdict = "REAL";
    explanation = `✓ VERIFIED: Found ${newsMatches.length} credible news source(s) reporting similar information. ML Model also supports this classification.`;
  } else if (finalScore < 40) {
    verdict = "FAKE";
    explanation = `❌ UNVERIFIED: Neither ML model nor major news sources confirm this story. This appears to be misinformation.`;
  } else if (finalScore < 60) {
    verdict = "UNVERIFIED";
    explanation = `⚠ PARTIALLY VERIFIED: Some claims may be true, but critical details lack credible news coverage. Recommend further research.`;
  } else {
    verdict = "REAL";
    explanation = `✓ LIKELY REAL: Article contains information found in credible news sources.`;
  }

  console.log("\n" + "=".repeat(60));
  console.log(`FINAL VERDICT: ${verdict}`);
  console.log(`CONFIDENCE: ${finalScore.toFixed(1)}%`);
  console.log("=".repeat(60) + "\n");

  return {
    verdict,
    confidence: Math.round(finalScore),
    explanation,
    mlPrediction,
    newsMatches: newsMatches.slice(0, 5),
  };
}

// ──────────────────────────────────────
// EXTRACT CLAIMS
// ──────────────────────────────────────
function extractClaims(text) {
  const sentences = text.match(/[^.!?]*[.!?]+/g) || [];
  return sentences
    .slice(0, 3)
    .map((s) => s.trim())
    .join(" ")
    .substring(0, 200);
}

// ──────────────────────────────────────
// POST /api/verify - MAIN ENDPOINT
// ──────────────────────────────────────
app.post("/api/verify", upload.single("file"), async (req, res) => {
  try {
    console.log("\n🔍 VERIFICATION REQUEST RECEIVED");
    
    let text = "";

    // Extract text from file or input
    if (req.file) {
      text = await extractText(req.file.path, req.file.originalname);
      if (text === "IMAGE_UPLOAD") {
        if (!req.body.title || req.body.title.trim() === "") {
          return res.status(400).json({
            error: "Images cannot be read. Please provide the article title.",
          });
        }
        text = req.body.title;
      }
    } else if (req.body.text) {
      text = req.body.text;
    } else {
      return res.status(400).json({ error: "No content provided" });
    }

    const title = (req.body.title || "").trim();
    const fullText = title ? `${title} ${text}` : text;

    if (!fullText || fullText.trim().length === 0) {
      return res.status(400).json({ error: "Content is empty" });
    }

    console.log(`📄 Article: "${fullText.substring(0, 100)}..."`);

    // Run real verification pipeline
    console.log("\n📡 RUNNING VERIFICATION PIPELINE...\n");

    // 1. ML Model Prediction
    const mlPrediction = await predictWithMLModel(fullText);

    // 2. Fetch Real News
    const searchQuery = title || extractClaims(text);
    const realNews = await fetchRealNews(searchQuery);

    // 3. Analyze and create verdict
    const result = await analyzeArticle(fullText, title, mlPrediction, realNews);

    // Return response
    res.json({
      verdict: result.verdict,
      confidence: result.confidence,
      explanation: result.explanation,
      mlPrediction: result.mlPrediction,
      matchingNews: result.newsMatches,
      totalNewsFound: result.newsMatches.length,
      query: searchQuery,
    });
  } catch (error) {
    console.error("❌ Verification error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ──────────────────────────────────────
// POST /api/ingest - STREAMING RESULTS
// ──────────────────────────────────────
app.post("/api/ingest", express.json(), (req, res) => {
  const { article, classification, confidence } = req.body;
  
  console.log(`\n📊 STREAMING RESULT: ${article?.headline}`);
  console.log(`   Verdict: ${classification} (${confidence}% confidence)`);
  
  res.json({ received: true });
});

// ──────────────────────────────────────
// HEALTH CHECK
// ──────────────────────────────────────
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    newsApiConfigured: !!process.env.NEWS_API_KEY,
    mlModelAvailable: fs.existsSync(path.join(__dirname, "../ml/model.pkl")),
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n${"=".repeat(60)}`);
  console.log(`✓ Server running on port ${PORT}`);
  console.log(`✓ NewsAPI configured: ${!!process.env.NEWS_API_KEY}`);
  console.log(`✓ ML Model available: ${fs.existsSync(path.join(__dirname, "../ml/model.pkl"))}`);
  console.log(`${"=".repeat(60)}\n`);
});
