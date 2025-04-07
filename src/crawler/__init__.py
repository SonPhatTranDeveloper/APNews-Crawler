import os
import pprint

from dotenv import load_dotenv

from src.model import CrawledNews, InitialNews
from src.news import get_headlines_by_source

from src.model import CrawledNews, InitialNews
import requests

from bs4 import BeautifulSoup


def crawl_ap_article(news: InitialNews) -> CrawledNews:
    # Call API
    payload = {"api_key": "57d662980d58e442b7d23ffc2dee710c", "url": news.url}
    r = requests.get("https://api.scraperapi.com/", params=payload)

    # Get the text and create soup
    html = r.text

    # Get a specific element
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", class_="RichTextBody")

    return CrawledNews(
        article=InitialNews(author=news.author, title=news.title, url=news.url),
        content=div.get_text(),
    )


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    from news import get_headlines_by_source

    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")

    news = get_headlines_by_source(api_key, "associated-press")

    first_news = crawl_ap_article(news[0])
    pprint.pprint(first_news)
