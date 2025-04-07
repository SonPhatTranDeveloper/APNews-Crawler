from src.model import CrawledNews, InitialNews
import requests
from bs4 import BeautifulSoup


def crawl_ap_article(news: InitialNews, api_key: str) -> CrawledNews:
    """Crawls an AP News article using ScraperAPI and extracts its main content.

    Args:
        news (InitialNews): The initial news metadata with URL.
        api_key (str): ScraperAPI key.

    Returns:
        CrawledNews: A structured result with metadata and article content.
    """
    # Prepare request payload
    params = {"api_key": api_key, "url": news.url}

    # Send GET request to ScraperAPI
    response = requests.get("https://api.scraperapi.com/", params=params)
    response.raise_for_status()

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="RichTextBody")

    # Extract text content
    content = content_div.get_text(strip=True) if content_div else ""

    return CrawledNews(
        article=InitialNews(
            author=news.author, title=news.title, url=news.url, imageUrl=news.imageUrl
        ),
        content=[content],
    )
