import os

from dotenv import load_dotenv
from tqdm import tqdm

from src.crawler import crawl_ap_article
from src.firebase import insert_document_firestore_rest, get_firestore_access_token
from src.llm import analyze_article_content
from src.news import get_headlines_by_source


def main():
    """Execute the code"""
    # Load the environment variables
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    service_account_location = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    # Get firebase token
    access_token = get_firestore_access_token(service_account_location)
    print("Access token obtained")

    # Get the news
    news = get_headlines_by_source(news_api_key, "associated-press")

    # Extract the content from the first news
    for article in tqdm(news):
        try:
            # Crawl the article
            crawled_article = crawl_ap_article(article)

            # Analyze the article
            analyzed_article = analyze_article_content(openai_api_key, crawled_article)

            # Insert it into the Firestore
            insert_document_firestore_rest(
                access_token=access_token,
                collection="articles",
                document_data=analyzed_article,
            )

        except Exception as e:
            print(f"Error inserting document: {e}")


if __name__ == "__main__":
    main()
