import requests
from bs4 import BeautifulSoup

from src.model import FullArticle, PartialArticle
from src.crawler.ap_news_crawler import BaseNewsCrawler


class TuoiTreNewsCrawler(BaseNewsCrawler):
    """A class for crawling Tuoi Tre News articles using ScraperAPI."""

    def __init__(self, api_key: str):
        """Initialize the TuoiTreNewsCrawler with a ScraperAPI key.

        Args:
            api_key (str): ScraperAPI key for making requests.
        """
        self.api_key = api_key

    def crawl_article(self, news: PartialArticle) -> FullArticle:
        """Crawls a Tuoi Tre News article using ScraperAPI and extracts its main content.

        Args:
            news (PartialArticle): The initial news metadata with URL.

        Returns:
            FullArticle: A structured result with metadata and article content.
        """
        # Prepare request payload
        params = {"api_key": self.api_key, "url": news.url}

        # Send GET request to ScraperAPI
        response = requests.get("https://api.scraperapi.com/", params=params)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="detail__main")

        # Extract text content
        content = content_div.get_text(strip=True) if content_div else ""

        return self._create_crawled_news(news, [content])
