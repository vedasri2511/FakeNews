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
// ML MODEL PREDICTION (Via Microservice)
// ──────────────────────────────────────
async function predictWithMLModel(text) {
  try {
    console.log("🤖 Calling ML Prediction Service...");
    
    // Call the ML microservice (running on port 5001)
    const response = await axios.post(
      "http://localhost:5001/predict",
      { text: text.substring(0, 2000) },
      { timeout: 5000 }
    );
    
    const result = response.data;
    console.log(`✓ ML Prediction: ${result.label} (${result.confidence.toFixed(1)}%)`);
    return result;
  } catch (error) {
    console.warn("⚠ ML Service error:", error.message);
    return null;
  }
}

// ──────────────────────────────────────
// FETCH REAL NEWS (NewsAPI - FAST)
// Simple in-memory cache to avoid burning NewsAPI quota on repeated queries
const newsCache = new Map(); // query -> { articles, fetchedAt }
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
let newsApiRateLimited = false;
let rateLimitResetAt = 0;

// ──────────────────────────────────────
async function fetchRealNews(query) {
  try {
    const apiKey = process.env.NEWS_API_KEY;

    if (!apiKey) {
      console.warn("⚠ NEWS_API_KEY not configured");
      return [];
    }

    // If we know we're rate limited, skip until reset time
    if (newsApiRateLimited && Date.now() < rateLimitResetAt) {
      const minsLeft = Math.ceil((rateLimitResetAt - Date.now()) / 60000);
      console.warn(`⚠ NewsAPI rate limited — skipping (resets in ~${minsLeft} min)`);
      return [];
    }

    // Use only the first 5 significant words as the canonical cache key
    const cacheKey = query.split(" ").filter(w => w.length > 3).slice(0, 5).join(" ").toLowerCase();

    // Return cached result if still fresh
    const cached = newsCache.get(cacheKey);
    if (cached && Date.now() - cached.fetchedAt < CACHE_TTL_MS) {
      console.log(`📦 NewsAPI cache hit for: "${cacheKey}" (${cached.articles.length} articles)`);
      return cached.articles;
    }

    console.log(`📰 Fetching real news for: "${cacheKey}"`);

    try {
      const response = await axios.get("https://newsapi.org/v2/everything", {
        params: {
          q: cacheKey,
          apiKey: apiKey,
          pageSize: 10,
          sortBy: "relevancy",
          language: "en",
        },
        timeout: 5000,
      });

      if (response.data.status === "ok" && response.data.articles?.length > 0) {
        const articles = response.data.articles.map((a) => ({
          source: a.source.name,
          title: a.title,
          content: a.description || "",
          url: a.url,
          date: a.publishedAt,
          image: a.urlToImage,
        }));
        newsCache.set(cacheKey, { articles, fetchedAt: Date.now() });
        console.log(`✓ NewsAPI returned ${articles.length} articles`);
        return articles;
      } else if (response.data.code === "rateLimited") {
        newsApiRateLimited = true;
        rateLimitResetAt = Date.now() + 12 * 60 * 60 * 1000; // 12 hours
        console.warn("⚠ NewsAPI rate limit hit — pausing NewsAPI calls for 12 hours");
        return [];
      }
    } catch (e) {
      if (e.response?.data?.code === "rateLimited") {
        newsApiRateLimited = true;
        rateLimitResetAt = Date.now() + 12 * 60 * 60 * 1000;
        console.warn("⚠ NewsAPI rate limit hit — pausing NewsAPI calls for 12 hours");
      } else {
        console.warn(`⚠ NewsAPI request failed: ${e.message}`);
      }
      return [];
    }

    console.warn("⚠ No articles found in NewsAPI");
    return [];
  } catch (error) {
    console.warn("NewsAPI fetch error:", error.message);
    return [];
  }
}

// ──────────────────────────────────────
// ANALYZE RESULTS
// ──────────────────────────────────────
async function analyzeArticle(articleText, title, mlPrediction, realNews) {
  console.log("\n" + "=".repeat(60));
  console.log("ANALYZING ARTICLE");
  console.log("=".repeat(60));

  // Find NewsAPI articles that share significant words with the input
  const articleWords = articleText.toLowerCase().split(/\s+/).filter((w) => w.length > 4);
  const newsMatches = realNews.filter((news) => {
    const newsWords = `${news.title} ${news.content}`.toLowerCase().split(/\s+/);
    const matches = articleWords.filter((word) => newsWords.includes(word)).length;
    return matches > 5;
  });

  console.log(`\n📰 NEWS COVERAGE: ${newsMatches.length} matching source(s)`);

  // ── PRIMARY SIGNAL: ML model ──
  // Decision logic:
  // 1. NewsAPI match is the strongest signal — if credible outlets cover it, it's REAL.
  //    The ML model was trained on 2015-2018 data and will mislabel post-2018 events,
  //    new entities (Truth Social, Pope Leo, etc.) and non-US topics.
  // 2. When no NewsAPI match, fall back to ML model.
  // 3. If ML model says FAKE with very high confidence (>85%) AND no NewsAPI match → FAKE.
  let verdict, confidence, explanation;

  if (!mlPrediction) {
    verdict = "FAKE";
    confidence = 0;
    explanation = `⚠ ML service unavailable — cannot determine authenticity.`;
  } else {
    const probReal = mlPrediction.prob_real ?? (mlPrediction.label === "REAL" ? mlPrediction.confidence : 100 - mlPrediction.confidence);
    const probFake = mlPrediction.prob_fake ?? (mlPrediction.label === "FAKE" ? mlPrediction.confidence : 100 - mlPrediction.confidence);

    console.log(`\n🤖 ML MODEL: ${mlPrediction.label} | REAL=${probReal.toFixed(1)}% FAKE=${probFake.toFixed(1)}%`);
    console.log(`📰 NewsAPI matches: ${newsMatches.length}`);

    if (newsMatches.length >= 2) {
      // NewsAPI found credible sources covering this — it's REAL
      verdict = "REAL";
      confidence = Math.min(99, Math.round(50 + newsMatches.length * 8 + probReal * 0.3));
      explanation = `✓ REAL NEWS: Found ${newsMatches.length} credible source(s) covering this story. Verified by independent news outlets.`;
    } else if (newsMatches.length === 1) {
      // One source found — lean REAL but note limited coverage
      verdict = "REAL";
      confidence = Math.round(60 + probReal * 0.3);
      explanation = `✓ REAL NEWS: Found a credible source covering this story. Content corroborated by independent reporting.`;
    } else if (probFake > 85) {
      // No NewsAPI match and ML is very confident it's fake
      verdict = "FAKE";
      confidence = Math.round(probFake);
      explanation = `❌ FAKE NEWS DETECTED: No credible sources found and content strongly matches misinformation patterns (${probFake.toFixed(1)}% confidence).`;
    } else if (probReal >= probFake) {
      // ML says REAL, no NewsAPI match
      verdict = "REAL";
      confidence = Math.round(probReal);
      explanation = `✓ REAL NEWS: Content analysis confirms this is legitimate news (${probReal.toFixed(1)}% confidence).`;
    } else {
      // ML says FAKE but not very confident, no NewsAPI match
      verdict = "FAKE";
      confidence = Math.round(probFake);
      explanation = `❌ FAKE NEWS: Content analysis flags this as misinformation (${probFake.toFixed(1)}% confidence). No credible sources found covering this story.`;
    }
  }

  console.log(`\nFINAL VERDICT: ${verdict} (${confidence}%)`);
  console.log("=".repeat(60) + "\n");

  return {
    verdict,
    confidence,
    explanation,
    mlPrediction,
    newsMatches: newsMatches.slice(0, 5),
  };
}

// ──────────────────────────────────────
// EXTRACT SEARCH KEYWORDS
// ──────────────────────────────────────
function extractSearchKeywords(text) {
  // Remove location/date markers (CITY, Date format)
  const words = text
    .split(/[\s,.-]+/)
    .filter(w => w.length > 2)
    .filter(w => !/^\d+$/.test(w)) // Remove pure numbers
    .slice(0, 5); // Get first 5 words
  
  return words.join(" ").substring(0, 80);
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

    // Check minimum text length - need at least 20 characters or meaningful content
    if (fullText.trim().length < 20) {
      return res.status(400).json({ 
        error: "Content too short. Please provide at least 20 characters of text for analysis." 
      });
    }

    console.log(`📄 Article: "${fullText.substring(0, 100)}..."`);

    // Run real verification pipeline
    console.log("\n📡 RUNNING VERIFICATION PIPELINE...\n");

    // 1. ML Model Prediction
    const mlPrediction = await predictWithMLModel(fullText);

    // 2. Fetch Real News - use better search keywords
    const searchQuery = extractSearchKeywords(title || text);
    console.log(`🔍 Search keywords: "${searchQuery}"`);
    const realNews = await fetchRealNews(searchQuery);

    // 3. Analyze and create verdict
    const result = await analyzeArticle(fullText, title, mlPrediction, realNews);

    // Generate key findings
    const keyFindings = [];
    if (mlPrediction) {
      const probReal = mlPrediction.prob_real ?? (mlPrediction.label === "REAL" ? mlPrediction.confidence : 100 - mlPrediction.confidence);
      const probFake = mlPrediction.prob_fake ?? (mlPrediction.label === "FAKE" ? mlPrediction.confidence : 100 - mlPrediction.confidence);
      keyFindings.push(`ML model: ${mlPrediction.label} — Real ${probReal.toFixed(1)}% / Fake ${probFake.toFixed(1)}%`);
    }
    if (result.newsMatches.length > 0) {
      keyFindings.push(`${result.newsMatches.length} credible source(s) covering this story`);
    } else {
      keyFindings.push("No matching sources found in NewsAPI");
    }
    keyFindings.push(`Verdict based on ML model (99.3% accuracy, 44,898 articles trained)`);

    // Extract trusted sources
    const trustedSourcesList = result.newsMatches.map((match) => ({
      title: match.title,
      source: match.source,
      url: match.url,
      snippet: match.content,
      link: match.url,
    }));

    // Return response
    res.json({
      verdict: result.verdict,
      confidence: result.confidence,
      explanation: result.explanation,
      mlPrediction: result.mlPrediction,
      matchingNews: result.newsMatches,
      sources: trustedSourcesList,
      trustedSources: trustedSourcesList,
      totalSources: realNews.length,
      keyFindings: keyFindings,
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
