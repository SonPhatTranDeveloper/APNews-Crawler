import os
import requests
from typing import List, Dict
from dotenv import load_dotenv


def get_headlines_by_source(api_key: str, source_id: str) -> List[Dict]:
    """Get the top headline from a particular source

    Args:
        api_key (_type_): API key of NewsAPI
        source_id (_type_): The string representation of the source

    Returns:
        _type_: A list of dictionary containing the news
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'sources': source_id,
        'apiKey': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        results = []
        for article in articles:
            results.append({
                'author': article.get('author'),
                'title': article.get('title'),
                'url': article.get('url')
            })
        return results
    else:
        print(f"Failed to fetch news: {response.status_code} - {response.text}")
        return []
    

if __name__ == "__main__":
    # Get environment key
    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")

    # Get the news
    news = get_headlines_by_source(api_key, "bbc-news")
    print(news)
