import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_articles(topic: str, max_articles: int = 10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print("NewsAPI error:", data.get("message"))
        return []

    articles = []
    for item in data.get("articles", []):
        content = item.get("content") or item.get("description") or ""
        if not content.strip():
            continue
        articles.append({
            "title": item["title"],
            "source": item["source"]["name"],
            "published": item["publishedAt"],
            "content": content,
            "url": item["url"]
        })

    return articles

def search_article_list(topic: str, max_articles: int = 8):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print("NewsAPI error:", data.get("message"))
        return []

    articles = []
    for item in data.get("articles", []):
        # Don't filter by content here — we only need metadata
        articles.append({
            "title": item["title"],
            "source": item["source"]["name"],
            "published": item["publishedAt"],
            "url": item["url"]
        })

    return articles
