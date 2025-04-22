from src.model import FullArticle, PartialArticle
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class BaseNewsCrawler(ABC):
    """Abstract base class for news crawlers."""

    @abstractmethod
    def crawl_article(self, news: PartialArticle) -> FullArticle:
        """Crawl a news article and extract its content.

        Args:
            news (PartialArticle): The initial news metadata with URL.

        Returns:
            FullArticle: A structured result with metadata and article content.
        """
        pass

    def _create_crawled_news(self, news: PartialArticle, content: list[str]) -> FullArticle:
        """Helper method to create a FullArticle object.

        Args:
            news (PartialArticle): The original news metadata.
            content (list[str]): The extracted article content.

        Returns:
            FullArticle: A structured result with metadata and content.
        """
        return FullArticle(
            article=PartialArticle(
                author=news.author,
                title=news.title,
                url=news.url,
                imageUrl=news.imageUrl
            ),
            content=content
        )


class APNewsCrawler(BaseNewsCrawler):
    """A class for crawling AP News articles using ScraperAPI."""

    def __init__(self, api_key: str):
        """Initialize the APNewsCrawler with a ScraperAPI key.

        Args:
            api_key (str): ScraperAPI key for making requests.
        """
        self.api_key = api_key

    def crawl_article(self, news: PartialArticle) -> FullArticle:
        """Crawls an AP News article using ScraperAPI and extracts its main content.

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
        content_div = soup.find("div", class_="RichTextBody")

        # Extract text content
        content = content_div.get_text(strip=True) if content_div else ""

        return self._create_crawled_news(news, [content]) 