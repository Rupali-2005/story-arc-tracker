from newspaper import Article
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_article(url: str) -> dict:
    try:
        article = Article(url, request_timeout=15, headers=HEADERS)
        article.download()
        article.parse()

        if not article.text.strip():
            return {"error": "Could not extract text from this URL. The site may be blocking scrapers. Try pasting the article text manually."}

        return {
            "title": article.title,
            "content": article.text,
            "source": article.source_url,
            "published": str(article.publish_date) if article.publish_date else "Unknown"
        }

    except Exception as e:
        return {"error": f"Could not fetch this article. The site may be blocking scrapers. Try pasting the article text manually."}
