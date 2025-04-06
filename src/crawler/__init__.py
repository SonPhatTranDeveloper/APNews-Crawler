import pprint
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.model import CrawledNews, InitialNews


def crawl_ap_article(news: InitialNews) -> CrawledNews:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(400)
    driver.get(news.url)
    time.sleep(2)

    paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.RichTextBody p")
    raw_text = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 5]
    content = " ".join(raw_text)

    driver.quit()

    return CrawledNews(
        article=InitialNews(
            author=news.author,
            title=news.title,
            url=news.url
        ),
        content=content
    )


if __name__ == "__main__":
    from news import get_headlines_by_source
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")

    news = get_headlines_by_source(api_key, "associated-press")

    first_news = crawl_ap_article(news[0])
    pprint.pprint(first_news)
