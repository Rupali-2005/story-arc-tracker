from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from analyzer import analyze_article
from fact_checker import check_claims
from news_fetcher import fetch_articles, search_article_list
from scraper import scrape_article
from report_generator import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Request Models ---

class TextInput(BaseModel):
    text: str

class URLInput(BaseModel):
    url: str

class TopicInput(BaseModel):
    topic: str
    max_articles: int = 5

class CompareInput(BaseModel):
    article_a: str
    article_b: str
    a_is_url: bool = False
    b_is_url: bool = False

class ReportInput(BaseModel):
    analysis: dict
    article_title: str = "Analyzed Article"
    report_name: str = "VeritasAI Report"


# --- Routes ---

@app.get("/")
def root():
    return {"status": "VeritasAI API is running"}


@app.post("/analyze")
def analyze(input: TextInput):
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        result = analyze_article(input.text)
        result["factual_claims"] = check_claims(result.get("factual_claims", []))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-url")
def analyze_url(input: URLInput):
    if not input.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    scraped = scrape_article(input.url)
    if "error" in scraped:
        raise HTTPException(status_code=400, detail=scraped["error"])

    try:
        result = analyze_article(scraped["content"])
        result["factual_claims"] = check_claims(result.get("factual_claims", []))
        result["article_title"] = scraped["title"]
        result["article_source"] = scraped["source"]
        result["article_url"] = input.url
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search-topic")
def search_topic(input: TopicInput):
    if not input.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        articles = search_article_list(input.topic, 8)
        if not articles:
            raise HTTPException(status_code=404, detail="No articles found for this topic")
        return {"topic": input.topic, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
def compare(input: CompareInput):
    try:
        if input.a_is_url:
            scraped_a = scrape_article(input.article_a)
            if "error" in scraped_a:
                raise HTTPException(status_code=400, detail=f"Article A: {scraped_a['error']}")
            content_a, title_a = scraped_a["content"], scraped_a["title"]
        else:
            content_a, title_a = input.article_a, "Article A"

        if input.b_is_url:
            scraped_b = scrape_article(input.article_b)
            if "error" in scraped_b:
                raise HTTPException(status_code=400, detail=f"Article B: {scraped_b['error']}")
            content_b, title_b = scraped_b["content"], scraped_b["title"]
        else:
            content_b, title_b = input.article_b, "Article B"

        result_a = analyze_article(content_a)
        result_b = analyze_article(content_b)
        result_a["factual_claims"] = check_claims(result_a.get("factual_claims", []))
        result_b["factual_claims"] = check_claims(result_b.get("factual_claims", []))

        score_a = result_a.get("overall_manipulation_score", 0)
        score_b = result_b.get("overall_manipulation_score", 0)

        if score_a > score_b:
            verdict = f"Article A is more manipulative by {round(score_a - score_b, 1)} points"
            more_biased = "A"
        elif score_b > score_a:
            verdict = f"Article B is more manipulative by {round(score_b - score_a, 1)} points"
            more_biased = "B"
        else:
            verdict = "Both articles are equally manipulative"
            more_biased = "none"

        return {
            "verdict": verdict,
            "more_biased": more_biased,
            "article_a": {"title": title_a, "url": input.article_a if input.a_is_url else None, "analysis": result_a},
            "article_b": {"title": title_b, "url": input.article_b if input.b_is_url else None, "analysis": result_b}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-report")
def generate_pdf_report(input: ReportInput):
    try:
        pdf_bytes = generate_report(input.analysis, input.article_title, input.report_name)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=veritasai-report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))