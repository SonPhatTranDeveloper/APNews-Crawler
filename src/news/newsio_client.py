from typing import List, Optional
from datetime import datetime

import requests

from src.model import PartialArticle
from src.news.newsapi_client import BaseNewsClient


class NewsIOAPIClient(BaseNewsClient):
    """NewsData.io implementation of the news client."""

    def __init__(self, api_key: str):
        """Initialize the NewsData.io client.

        Args:
            api_key (str): API key for NewsData.io.
        """
        self.api_key = api_key
        self.base_url = "https://newsdata.io/api/1/latest"

    def _parse_author(self, article: dict) -> str:
        """Parse author from article data.

        Args:
            article (dict): Article data from API response.

        Returns:
            str: Author name or source name if author not available.
        """
        if article.get("creator"):
            if isinstance(article["creator"], list):
                return ", ".join(filter(None, article["creator"]))
            return str(article["creator"])
        return article.get("source_id", "Unknown")

    def get_headlines(self, source_id: str, total: int = 10) -> List[PartialArticle]:
        """Get headlines from a news source using NewsData.io API.

        Args:
            source_id (str): The ID of the news source (domain name).
            total (int): The total number of headlines to fetch.

        Returns:
            List[PartialArticle]: A list of news headlines.
        """
        params = {
            "domain": source_id,
            "apikey": self.api_key,
            "size": str(total),
            "country": "vi",  # Hardcoded for Vietnamese news
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching headlines: {e}")
            return []

        data = response.json()
        if data.get("status") != "success":
            print(f"API returned error status: {data.get('status')}")
            return []

        if data.get("totalResults", 0) == 0:
            print("No articles found")
            return []

        articles = data.get("results", [])
        return [
            PartialArticle(
                author=self._parse_author(article),
                title=article.get("title", "").strip(),
                url=article.get("link", ""),
                imageUrl=article.get("image_url", ""),
            )
            for article in articles
            if article.get("title")
            and article.get("link")  # Only include articles with required fields
        ]
