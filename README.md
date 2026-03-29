# VeritasAI — AI-Powered Media Bias Detector

> ET AI Hackathon 2026 | Problem Statement 8 — AI-Native News Experience  
[https://veritasai-frontend-58z8.onrender.com/]
## What It Does

VeritasAI analyzes news articles to detect manipulation techniques, 
logical fallacies, and political bias — then explains them in plain 
English and suggests cleaner alternatives.

Most people consume news passively. VeritasAI makes them active, 
critical readers.

## Core Features

- Detects 13 manipulation techniques across 4 categories
- Severity scoring (1-10) for each detected pattern
- Political leaning classification with confidence score
- Factual claim extraction and verification
- Plain English explanation of every fallacy detected
- Clean rewrite of the article removing all bias
- Article comparison mode — compare two sources on same topic
- Real-time article search by topic via NewsAPI
- URL scraping — paste any article link and analyze instantly

## Tech Stack

- Backend: Python + FastAPI
- AI: Groq API (LLaMA 3.3 70B)
- News Data: NewsAPI
- Web Scraping: newspaper3k
- Fact Checking: Google Fact Check API
- Frontend: HTML, CSS, Vanilla JavaScript
- Deployed: Railway (backend) + Vercel (frontend)

## How To Run Locally
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `frontend/index.html` in your browser.

## Architecture
```
User Input (text / URL / topic search)
               ↓
Scraper Module — extracts article content
               ↓
Analyzer Agent — detects manipulation via taxonomy
               ↓
Fact Checker — verifies claims via Google API
               ↓
Report Generator — structured results + rewrite
               ↓
Frontend — renders results with severity indicators
```

## ET Business Case

Reader trust is ET's core asset. VeritasAI gives ET readers a tool 
to evaluate the credibility of market-moving articles before making 
investment decisions — making ET the only platform that actively 
builds media literacy, not just delivers content.

**Impact estimate:**
- Average ET Markets reader consumes 8-12 articles daily
- 1 manipulative article acting on = potential financial loss
- VeritasAI adds a critical thinking layer that no competitor offers
