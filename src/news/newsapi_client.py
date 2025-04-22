from typing import List

import requests

from abc import ABC, abstractmethod
from typing import List

from src.model import PartialArticle


class BaseNewsClient(ABC):
    """Abstract base class for news operations."""

    @abstractmethod
    def get_headlines(self, source_id: str, total: int = 10) -> List[PartialArticle]:
        """Get headlines from a news source.

        Args:
            source_id (str): The ID of the news source.
            total (int): The total number of headlines to fetch.

        Returns:
            List[PartialArticle]: A list of news headlines.
        """
        pass


class NewsAPIClient(BaseNewsClient):
    """NewsAPI implementation of the news client."""

    def __init__(self, api_key: str):
        """Initialize the NewsAPI client.

        Args:
            api_key (str): API key for NewsAPI.
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def get_headlines(self, source_id: str, total: int = 10) -> List[PartialArticle]:
        """Get headlines from a news source using NewsAPI.

        Args:
            source_id (str): The ID of the news source.
            total (int): The total number of headlines to fetch.

        Returns:
            List[PartialArticle]: A list of news headlines.
        """
        params = {"sources": source_id, "apiKey": self.api_key, "pageSize": str(total)}

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching headlines: {e}")
            return []

        articles = response.json().get("articles", [])
        return [
            PartialArticle(
                author=article.get("author"),
                title=article.get("title"),
                url=article.get("url"),
                imageUrl=article.get("urlToImage"),
            )
            for article in articles
        ]
