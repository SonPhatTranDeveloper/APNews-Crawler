import os

from dotenv import load_dotenv
from tqdm import tqdm

from src.crawler import crawl_ap_article
from src.firebase import insert_document
from src.llm import analyze_article_content
from src.news import get_headlines_by_source


def main():
    """Execute the code"""
    # Load the environment variables
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    service_account_location = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    # Get the news
    news = get_headlines_by_source(news_api_key, "associated-press")

    # Extract the content from the first news
    for article in tqdm(news):
        # Crawl the article
        crawled_article = crawl_ap_article(article)

        # Analyze the article
        analyzed_article = analyze_article_content(openai_api_key, crawled_article)

        # Insert it into the Firestore
        insert_document(
            service_account_path=service_account_location,
            collection_name="articles",
            data=analyzed_article,
        )


if __name__ == "__main__":
    main()
