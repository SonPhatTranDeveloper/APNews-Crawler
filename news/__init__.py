


def get_headlines_by_source(api_key, source_id):
    """_summary_

    Args:
        api_key (_type_): _description_
        source_id (_type_): _description_

    Returns:
        _type_: _description_
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