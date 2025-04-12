import os
import pprint

from dotenv import load_dotenv
from tqdm import tqdm

from constants import FIREBASE_COLLECTION, NEWS_SOURCE
from src.crawler import crawl_ap_article
from src.firebase import get_firestore_access_token, insert_document_firestore_rest
from src.llm import analyze_article_content
from src.news import get_headlines_by_source
from src.utils import url_to_document_id


def load_api_keys():
    """Load environment variables and return necessary API keys and credentials."""
    load_dotenv()
    return {
        "news_api_key": os.getenv("NEWS_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "scraper_api_key": os.getenv("SCRAPER_API_KEY"),
        "service_account_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    }


def process_article(article, scraper_key, openai_key, access_token):
    """Crawl, analyze, and insert a single article into Firestore."""
    # Crawl content using ScraperAI
    crawled = crawl_ap_article(article, api_key=scraper_key)

    # Analyze the article content using ChatGPT
    analyzed = analyze_article_content(crawled, api_key=openai_key)
    pprint.pprint(analyzed)

    # Get the URL from document and encode
    encoded_url = url_to_document_id(analyzed["url"])

    # Insert document
    insert_document_firestore_rest(
        access_token=access_token,
        collection=FIREBASE_COLLECTION,
        document_id=encoded_url,
        document_data=analyzed,
    )


def main():
    """Main execution flow."""
    keys = load_api_keys()

    access_token = get_firestore_access_token(keys["service_account_path"])
    print("Firebase access token obtained.")

    articles = get_headlines_by_source(NEWS_SOURCE, keys["news_api_key"], total=5)

    for article in tqdm(articles, desc="Processing articles"):
        try:
            process_article(
                article,
                scraper_key=keys["scraper_api_key"],
                openai_key=keys["openai_api_key"],
                access_token=access_token,
            )
        except Exception as e:
            print(f"Failed to process article: {e}")


if __name__ == "__main__":
    main()
