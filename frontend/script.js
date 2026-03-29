const API = "https://veritasai-frontend.onrender.com";

// --- Tab Switching ---
function switchTab(tab) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.getElementById("paste-tab").style.display = "none";
  document.getElementById("url-tab").style.display = "none";
  document.getElementById("topic-tab").style.display = "none";
  document.getElementById("compare-tab").style.display = "none";

  if (tab === "paste") {
    document.getElementById("paste-tab").style.display = "block";
    document.querySelectorAll(".tab")[0].classList.add("active");
  } else if (tab === "url") {
    document.getElementById("url-tab").style.display = "block";
    document.querySelectorAll(".tab")[1].classList.add("active");
  } 
  else if (tab === "compare") {
    document.getElementById("compare-tab").style.display = "block";
    document.querySelectorAll(".tab")[3].classList.add("active");
  }
  else {
    document.getElementById("topic-tab").style.display = "block";
    document.querySelectorAll(".tab")[2].classList.add("active");
  }
} 


// --- Analyze Pasted Text ---
async function analyzeText() {
  const text = document.getElementById("article-input").value.trim();
  if (!text) return alert("Please paste an article first.");

  showLoader();

  try {
    const res = await fetch(`${API}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    alert("Something went wrong. Make sure your backend is running.");
    console.error(err);
  }

  hideLoader();
}

async function analyzeURL() {
  const url = document.getElementById("url-input").value.trim();
  if (!url) return alert("Please paste a URL first.");

  showLoader();

  try {
    const res = await fetch(`${API}/analyze-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (data.detail) {
      alert("Error: " + data.detail);
    } else {
      // Show article title if available
      if (data.article_title) {
        document.querySelector("header p").textContent =
          `Analyzing: ${data.article_title}`;
      }
      renderResults(data);
    }
  } catch (err) {
    alert("Something went wrong. Make sure your backend is running.");
    console.error(err);
  }

  hideLoader();
}
async function searchTopic() {
  const topic = document.getElementById("topic-input").value.trim();
  if (!topic) return alert("Please enter a topic.");

  showLoader();

  try {
    const res = await fetch(`${API}/search-topic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, max_articles: 8 })
    });
    const data = await res.json();

    if (data.detail) {
      alert("Error: " + data.detail);
    } else {
      renderArticleList(data.articles);
    }
  } catch (err) {
    alert("Something went wrong. Make sure your backend is running.");
    console.error(err);
  }

  hideLoader();
}

function renderArticleList(articles) {
  const container = document.getElementById("article-list");
  container.style.display = "block";

  container.innerHTML = `
    <p style="color:#888; font-size:0.88rem; margin-bottom:12px;">
      ${articles.length} articles found. Pick one:
    </p>
    ${articles.map((a) => `
      <div class="article-card">
        <div class="article-card-source">${a.source} · ${formatDate(a.published)}</div>
        <div class="article-card-title">${a.title}</div>
        <div style="display:flex; gap:10px; margin-top:10px;">
          <button 
            onclick="analyzeFromList('${encodeURIComponent(a.url)}', '${encodeURIComponent(a.title)}')"
            style="flex:1; padding:8px; background:#4f6ef7; color:white; border:none; border-radius:8px; cursor:pointer; font-size:0.85rem;">
            🔍 Analyze
          </button>
          <a 
            href="${a.url}" 
            target="_blank"
            style="flex:1; padding:8px; background:#1a1d2e; color:#4f6ef7; border:1px solid #4f6ef7; border-radius:8px; cursor:pointer; font-size:0.85rem; text-align:center; text-decoration:none;">
            📄 Read Full Article
          </a>
        </div>
      </div>
    `).join("")}
  `;
}

async function analyzeFromList(encodedUrl, encodedTitle) {
  const url = decodeURIComponent(encodedUrl);
  const title = decodeURIComponent(encodedTitle);

  document.getElementById("article-list").style.display = "none";
  showLoader();

  try {
    const res = await fetch(`${API}/analyze-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (data.detail) {
      alert("Error: " + data.detail);
    } else {
      document.querySelector("header p").textContent = `Analyzing: ${title}`;
      renderResults(data);
    }
  } catch (err) {
    alert("Something went wrong. Make sure your backend is running.");
    console.error(err);
  }

  hideLoader();
}

function formatDate(dateStr) {
  if (!dateStr) return "Unknown date";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function renderResults(data) {
  document.getElementById("results").style.display = "block";
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });

  const existingLink = document.getElementById("article-source-link");
  if (existingLink) existingLink.remove();

  if (data.article_url || data.article_source) {
    const url = data.article_url || data.article_source;
    const linkDiv = document.createElement("div");
    linkDiv.id = "article-source-link";
    linkDiv.style.cssText = "margin-bottom:16px; padding:14px; background:#1a1d2e; border-radius:10px; border:1px solid #2a2d3e;";
    linkDiv.innerHTML = `
      <span style="color:#888; font-size:0.85rem;">Source article: </span>
      <a href="${url}" target="_blank" style="color:#4f6ef7; font-size:0.85rem; word-break:break-all;">${url}</a>
    `;
    document.getElementById("results").prepend(linkDiv);
  }

  renderScore(data.overall_manipulation_score);
  renderLeaning(data.political_leaning);
  renderSummary(data.rhetorical_summary);
  renderPatterns(data.detected_patterns);
  renderClaims(data.factual_claims);
  renderRewrite(data.clean_rewrite);
  renderDownloadButton(data);
}


// --- Score Bar ---
function renderScore(score) {
  const pct = (score / 10) * 100;
  const bar = document.getElementById("score-bar");
  const label = document.getElementById("score-label");

  bar.style.width = pct + "%";

  if (score <= 3) {
    bar.style.background = "#4caf80";
    label.textContent = `${score.toFixed(1)} / 10 — Low manipulation. Mostly clean.`;
  } else if (score <= 6) {
    bar.style.background = "#f0a500";
    label.textContent = `${score.toFixed(1)} / 10 — Moderate manipulation. Read critically.`;
  } else {
    bar.style.background = "#e05c5c";
    label.textContent = `${score.toFixed(1)} / 10 — High manipulation. Be very skeptical.`;
  }
}

// --- Political Leaning ---
function renderLeaning(leaning) {
  if (!leaning) return;

  const positions = {
    "Left": 5,
    "Centre-Left": 25,
    "Neutral": 50,
    "Centre-Right": 75,
    "Right": 95
  };

  const pos = positions[leaning.label] || 50;
  const signals = leaning.key_signals || [];

  document.getElementById("leaning-content").innerHTML = `
    <div class="leaning-bar">
      <span>Left</span>
      <span>Centre</span>
      <span>Right</span>
    </div>
    <div class="leaning-indicator">
      <div class="leaning-dot" style="left: ${pos}%"></div>
    </div>
    <p style="font-size:0.9rem; color:#ccc; margin-bottom:10px;">
      <strong style="color:#fff">${leaning.label}</strong> — ${leaning.confidence}% confidence
    </p>
    <div class="signals">
      ${signals.map(s => `<span class="signal-tag">${s}</span>`).join("")}
    </div>
  `;
}

// --- Rhetorical Summary ---
function renderSummary(summary) {
  document.getElementById("rhetorical-summary").textContent = summary || "No summary available.";
}

// --- Detected Patterns ---
function renderPatterns(patterns) {
  const container = document.getElementById("patterns-list");

  if (!patterns || patterns.length === 0) {
    container.innerHTML = "<p style='color:#888'>No manipulation patterns detected.</p>";
    return;
  }

  container.innerHTML = patterns.map(p => {
    const severity = p.severity || 0;
    const level = severity >= 7 ? "high" : severity >= 4 ? "medium" : "low";
    const badgeColor = level === "high" ? "#e05c5c" : level === "medium" ? "#f0a500" : "#4caf80";

    return `
      <div class="pattern ${level}">
        <h3>${p.category} — ${p.subcategory}</h3>
        <div class="quote">"${p.quote}"</div>
        <p><strong style="color:#fff">What this is:</strong> ${p.what_this_means}</p>
        <p><strong style="color:#fff">Why it's a problem:</strong> ${p.why_its_problematic}</p>
        <span class="severity-badge" style="background:${badgeColor}22; color:${badgeColor}">
          Severity: ${severity}/10
        </span>
      </div>
    `;
  }).join("");
}

// --- Factual Claims ---
function renderClaims(claims) {
  const container = document.getElementById("claims-list");

  if (!claims || claims.length === 0) {
    container.innerHTML = "<p style='color:#888'>No factual claims extracted.</p>";
    return;
  }

  container.innerHTML = claims.map(c => {
    const verdict = c.verdict || "Unverifiable";
    let cls = "unverifiable";
    if (verdict.includes("True")) cls = "true";
    else if (verdict.includes("False")) cls = "false";
    else if (verdict.includes("Expert")) cls = "needs";

    const source = c.source
      ? `<a href="${c.source}" target="_blank" style="color:#4f6ef7; font-size:0.8rem;">View source</a>`
      : "";

    return `
      <div class="claim">
        <p>${c.claim}</p>
        <span class="verdict ${cls}">${verdict}</span>
        ${source}
      </div>
    `;
  }).join("");
}

// --- Clean Rewrite ---
function renderRewrite(rewrite) {
  document.getElementById("clean-rewrite").textContent = rewrite || "No rewrite available.";
}

// --- Helpers ---
function showLoader() {
  document.getElementById("loader").style.display = "block";
  document.getElementById("results").style.display = "none";
}

function hideLoader() {
  document.getElementById("loader").style.display = "none";
}

// --- Toggle text/url input for compare ---
function toggleInput(article, type) {
  const textEl = document.getElementById(`compare-${article}-text`);
  const urlEl = document.getElementById(`compare-${article}-url`);
  const textBtn = document.getElementById(`toggle-${article}-text`);
  const urlBtn = document.getElementById(`toggle-${article}-url`);

  if (type === "text") {
    textEl.style.display = "block";
    urlEl.style.display = "none";
    textBtn.classList.add("active");
    urlBtn.classList.remove("active");
  } else {
    textEl.style.display = "none";
    urlEl.style.display = "block";
    urlBtn.classList.add("active");
    textBtn.classList.remove("active");
  }
}

// --- Compare Articles ---
async function compareArticles() {
  const aIsUrl = document.getElementById("toggle-a-url").classList.contains("active");
  const bIsUrl = document.getElementById("toggle-b-url").classList.contains("active");

  const articleA = aIsUrl
    ? document.getElementById("compare-a-url").value.trim()
    : document.getElementById("compare-a-text").value.trim();

  const articleB = bIsUrl
    ? document.getElementById("compare-b-url").value.trim()
    : document.getElementById("compare-b-text").value.trim();

  if (!articleA) return alert("Please provide Article A.");
  if (!articleB) return alert("Please provide Article B.");

  showLoader();
  document.getElementById("compare-results").style.display = "none";

  try {
    const res = await fetch(`${API}/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        article_a: articleA,
        article_b: articleB,
        a_is_url: aIsUrl,
        b_is_url: bIsUrl
      })
    });

    const data = await res.json();
    if (data.detail) return alert("Error: " + data.detail);
    renderComparison(data);

  } catch (err) {
    alert("Something went wrong. Make sure your backend is running.");
    console.error(err);
  }

  hideLoader();
}

// --- Render Comparison ---
function renderComparison(data) {
  document.getElementById("compare-results").style.display = "block";
  document.getElementById("compare-results").scrollIntoView({ behavior: "smooth" });

  // Verdict
  const verdictEl = document.getElementById("compare-verdict");
  verdictEl.textContent = data.verdict;
  verdictEl.className = "verdict-banner";
  if (data.more_biased === "A") {
    verdictEl.classList.add("a-wins");
    document.getElementById("compare-col-a").classList.add("highlight");
    document.getElementById("compare-col-b").classList.remove("highlight");
  } else if (data.more_biased === "B") {
    verdictEl.classList.add("b-wins");
    document.getElementById("compare-col-b").classList.add("highlight");
    document.getElementById("compare-col-a").classList.remove("highlight");
  } else {
    verdictEl.classList.add("tie");
  }

  // Titles
  document.getElementById("compare-title-a").textContent = data.article_a.title || "Article A";
  document.getElementById("compare-title-b").textContent = data.article_b.title || "Article B";

  // Scores
  renderScoreFor(data.article_a.analysis.overall_manipulation_score, "a");
  renderScoreFor(data.article_b.analysis.overall_manipulation_score, "b");

  // Leanings
  renderLeaningFor(data.article_a.analysis.political_leaning, "a");
  renderLeaningFor(data.article_b.analysis.political_leaning, "b");

  // Summaries
  document.getElementById("rhetorical-summary-a").textContent =
    data.article_a.analysis.rhetorical_summary || "";
  document.getElementById("rhetorical-summary-b").textContent =
    data.article_b.analysis.rhetorical_summary || "";

  // Patterns
  renderPatternsFor(data.article_a.analysis.detected_patterns, "a");
  renderPatternsFor(data.article_b.analysis.detected_patterns, "b");
}

function renderScoreFor(score, side) {
  const pct = (score / 10) * 100;
  const bar = document.getElementById(`score-bar-${side}`);
  const label = document.getElementById(`score-label-${side}`);
  bar.style.width = pct + "%";
  if (score <= 3) {
    bar.style.background = "#4caf80";
    label.textContent = `${score.toFixed(1)} / 10 — Low manipulation.`;
  } else if (score <= 6) {
    bar.style.background = "#f0a500";
    label.textContent = `${score.toFixed(1)} / 10 — Moderate manipulation.`;
  } else {
    bar.style.background = "#e05c5c";
    label.textContent = `${score.toFixed(1)} / 10 — High manipulation.`;
  }
}

function renderLeaningFor(leaning, side) {
  if (!leaning) return;
  const positions = {
    "Left": 5, "Centre-Left": 25,
    "Neutral": 50, "Centre-Right": 75, "Right": 95
  };
  const pos = positions[leaning.label] || 50;
  document.getElementById(`leaning-content-${side}`).innerHTML = `
    <div class="leaning-bar">
      <span>Left</span><span>Centre</span><span>Right</span>
    </div>
    <div class="leaning-indicator">
      <div class="leaning-dot" style="left:${pos}%"></div>
    </div>
    <p style="font-size:0.9rem; color:#ccc; margin-bottom:10px;">
      <strong style="color:#fff">${leaning.label}</strong> — ${leaning.confidence}% confidence
    </p>
    <div class="signals">
      ${(leaning.key_signals || []).map(s => `<span class="signal-tag">${s}</span>`).join("")}
    </div>
  `;
}

function renderPatternsFor(patterns, side) {
  const container = document.getElementById(`patterns-list-${side}`);
  if (!patterns || patterns.length === 0) {
    container.innerHTML = "<p style='color:#888'>No manipulation patterns detected.</p>";
    return;
  }
  container.innerHTML = patterns.map(p => {
    const severity = p.severity || 0;
    const level = severity >= 7 ? "high" : severity >= 4 ? "medium" : "low";
    const badgeColor = level === "high" ? "#e05c5c" : level === "medium" ? "#f0a500" : "#4caf80";
    return `
      <div class="pattern ${level}">
        <h3>${p.category} — ${p.subcategory}</h3>
        <div class="quote">"${p.quote}"</div>
        <p><strong style="color:#fff">What this is:</strong> ${p.what_this_means}</p>
        <p><strong style="color:#fff">Why it's a problem:</strong> ${p.why_its_problematic}</p>
        <span class="severity-badge" style="background:${badgeColor}22; color:${badgeColor}">
          Severity: ${severity}/10
        </span>
      </div>
    `;
  }).join("");
}

function renderDownloadButton(data) {
  const existing = document.getElementById("download-btn-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "download-btn-container";
  container.style.cssText = "text-align:center; margin-top:24px; padding:20px; background:#1a1d2e; border-radius:12px; border:1px solid #2a2d3e;";
  container.innerHTML = `
    <p style="color:#aaa; font-size:0.88rem; margin-bottom:10px;">Name your report before downloading:</p>
    <input 
      type="text" 
      id="report-name-input"
      value="VeritasAI Analysis Report"
      style="width:60%; padding:10px; background:#12151f; border:1px solid #2a2d3e; border-radius:8px; color:#fff; font-size:0.9rem; text-align:center; margin-bottom:14px;"
    />
    <br/>
    <button 
      onclick="downloadReport()"
      style="padding:14px 40px; background:#4f6ef7; color:white; border:none; border-radius:10px; font-size:1rem; cursor:pointer;">
      Download Full Report (PDF)
    </button>
  `;
  document.getElementById("results").appendChild(container);
  window._lastAnalysis = data;
}

async function downloadReport() {
  if (!window._lastAnalysis) return alert("No analysis to download.");

  const reportName = document.getElementById("report-name-input")?.value || "VeritasAI Report";
  const fileName = reportName.replace(/[^a-z0-9\s]/gi, "").replace(/\s+/g, "-").toLowerCase() + ".pdf";

  try {
    const res = await fetch(`${API}/generate-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis: window._lastAnalysis,
        article_title: window._lastAnalysis.article_title || "Analyzed Article",
        report_name: reportName
      })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);

  } catch (err) {
    alert("Could not generate report. Try again.");
    console.error(err);
  }
}
async function downloadReport() {
  if (!window._lastAnalysis) return alert("No analysis to download.");

  try {
    const res = await fetch(`${API}/generate-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis: window._lastAnalysis,
        article_title: window._lastAnalysis.article_title || "Analyzed Article"
      })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "VeritasAI-report.pdf";
    a.click();
    URL.revokeObjectURL(url);

  } catch (err) {
    alert("Could not generate report. Try again.");
    console.error(err);
  }
}
