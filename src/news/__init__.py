from typing import List

from src.model import PartialArticle
from .newsapi_client import NewsAPIClient


def get_headlines_by_source(
    source_id: str,
    api_key: str,
    total: int = 10,
) -> List[PartialArticle]:
    """Legacy function that uses NewsAPIClient internally.
    
    Args:
        source_id (str): The ID of the news source.
        api_key (str): API key for NewsAPI.
        total (int): The total number of headlines to fetch.
        
    Returns:
        List[PartialArticle]: A list of news headlines.
    """
    client = NewsAPIClient(api_key)
    return client.get_headlines(source_id, total)
