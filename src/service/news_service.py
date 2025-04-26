from abc import ABC, abstractmethod
from typing import List

from src.model import FullArticle
from src.news import BaseNewsClient, NewsAPIClient
from src.crawler import BaseNewsCrawler, APNewsCrawler

from src.news.newsio_client import NewsIOAPIClient
from src.crawler.tuoitre_news_crawler import TuoiTreNewsCrawler


class BaseNewsService(ABC):
    """Abstract base class for combined news operations."""

    @abstractmethod
    def get_full_articles(self, source_id: str, total: int = 10) -> List[FullArticle]:
        """Get full articles including content from a news source.

        Args:
            source_id (str): The ID of the news source.
            total (int): The total number of articles to fetch.

        Returns:
            List[FullArticle]: A list of full articles with content.
        """
        pass


class DefaultNewsService(BaseNewsService):
    """Default implementation of news service that combines NewsAPI and AP News crawler."""

    def __init__(self, news_api_key: str, scraper_api_key: str):
        """Initialize the NewsService with required API keys.

        Args:
            news_api_key (str): API key for NewsAPI.
            scraper_api_key (str): API key for ScraperAPI.
        """
        self.news_client = NewsAPIClient(news_api_key)
        self.crawler = APNewsCrawler(scraper_api_key)

    def get_full_articles(self, source_id: str, total: int = 10) -> List[FullArticle]:
        """Get full articles including content from a news source.

        Args:
            source_id (str): The ID of the news source.
            total (int): The total number of articles to fetch.

        Returns:
            List[FullArticle]: A list of full articles with content.
        """
        # Get headlines first
        partial_articles = self.news_client.get_headlines(source_id, total)

        # Crawl content for each article
        full_articles = []
        for article in partial_articles:
            try:
                full_article = self.crawler.crawl_article(article)
                full_articles.append(full_article)
            except Exception as e:
                print(f"Error crawling article {article.url}: {e}")
                continue

        return full_articles


class VietnameseNewsService(BaseNewsService):
    """Vietnamese news service that combines NewsIO API and Tuoi Tre News crawler."""

    def __init__(self, news_io_api_key: str, scraper_api_key: str):
        """Initialize the VietnameseNewsService with required API keys.

        Args:
            news_io_api_key (str): API key for NewsIO API.
            scraper_api_key (str): API key for ScraperAPI.
        """
        self.news_client = NewsIOAPIClient(news_io_api_key)
        self.crawler = TuoiTreNewsCrawler(scraper_api_key)

    def get_full_articles(self, source_id: str, total: int = 10) -> List[FullArticle]:
        """Get full articles including content from a Vietnamese news source.

        Args:
            source_id (str): The domain of the news source (e.g., 'tuoitre.vn').
            total (int): The total number of articles to fetch.

        Returns:
            List[FullArticle]: A list of full articles with content.
        """
        # Get headlines first
        partial_articles = self.news_client.get_headlines(source_id, total)

        # Crawl content for each article
        full_articles = []
        for article in partial_articles:
            try:
                full_article = self.crawler.crawl_article(article)
                full_articles.append(full_article)
            except Exception as e:
                print(f"Error crawling article {article.url}: {e}")
                continue

        return full_articles


class CustomNewsService(BaseNewsService):
    """Customizable implementation of news service that allows injection of any news client and crawler."""

    def __init__(self, news_client: BaseNewsClient, crawler: BaseNewsCrawler):
        """Initialize the NewsService with custom implementations.

        Args:
            news_client (BaseNewsClient): Any implementation of BaseNewsClient.
            crawler (BaseNewsCrawler): Any implementation of BaseNewsCrawler.
        """
        self.news_client = news_client
        self.crawler = crawler

    def get_full_articles(self, source_id: str, total: int = 10) -> List[FullArticle]:
        """Get full articles including content from a news source.

        Args:
            source_id (str): The ID of the news source.
            total (int): The total number of articles to fetch.

        Returns:
            List[FullArticle]: A list of full articles with content.
        """
        # Get headlines first
        partial_articles = self.news_client.get_headlines(source_id, total)

        # Crawl content for each article
        full_articles = []
        for article in partial_articles:
            try:
                full_article = self.crawler.crawl_article(article)
                full_articles.append(full_article)
            except Exception as e:
                print(f"Error crawling article {article.url}: {e}")
                continue

        return full_articles
