import os
from typing import List

import requests
from dotenv import load_dotenv

from src.model import InitialNews


def get_headlines_by_source(api_key: str, source_id: str) -> List[InitialNews]:
    """Get the top headline from a particular source

    Args:
        api_key (_type_): API key of NewsAPI
        source_id (_type_): The string representation of the source

    Returns:
        _type_: A list of dictionary containing the news
    """
    # Define URL and parameters
    url = "https://newsapi.org/v2/top-headlines"
    params = {"sources": source_id, "apiKey": api_key}

    # Get the response
    response = requests.get(url, params=params)

    # If successful, parse the response
    # Else display and error and return an empty array
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])

        results = []
        for article in articles:

            results.append(
                InitialNews(
                    author=article.get("author"),
                    title=article.get("title"),
                    url=article.get("url"),
                )
            )

        return results
    else:
        print(f"Failed to fetch news: {response.status_code} - {response.text}")
        return []
