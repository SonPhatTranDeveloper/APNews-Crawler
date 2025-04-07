import os
import pprint

from dotenv import load_dotenv

from src.model import CrawledNews, InitialNews
from src.news import get_headlines_by_source

from src.model import CrawledNews, InitialNews
import requests

from bs4 import BeautifulSoup


def crawl_ap_article(news: InitialNews, api_key: str) -> CrawledNews:
    # Call API
    payload = {"api_key": api_key, "url": news.url}
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
