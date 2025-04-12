from typing import List

import requests

from src.model import InitialNews


def get_headlines_by_source(
    source_id: str,
    api_key: str,
    total: int = 10,
) -> List[InitialNews]:
    """
    Fetch the top headlines from a specific news source using NewsAPI.

    Args:
        api_key (str): API key for NewsAPI.
        source_id (str): The ID of the news source.
        total (int): The total number of news

    Returns:
        List[InitialNews]: A list of news headlines as InitialNews objects.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {"sources": source_id, "apiKey": api_key, "pageSize": str(total)}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching headlines: {e}")
        return []

    articles = response.json().get("articles", [])
    return [
        InitialNews(
            author=article.get("author"),
            title=article.get("title"),
            url=article.get("url"),
            imageUrl=article.get("urlToImage"),
        )
        for article in articles
    ]
