import os
import pprint
from typing import Dict

from dotenv import load_dotenv
from tqdm import tqdm

from constants import FIREBASE_COLLECTION, NEWS_SOURCE
from src.crawler import APNewsCrawler
from src.firebase import FirestoreClient
from src.llm import OpenAIArticleAnalyzer
from src.news import NewsAPIClient
from src.utils import url_to_document_id


class NewsProcessor:
    """Class to handle the news processing pipeline."""

    def __init__(self, api_keys: Dict[str, str]):
        """Initialize the news processor with API keys.

        Args:
            api_keys (Dict[str, str]): Dictionary containing all required API keys.
        """
        self.api_keys = api_keys
        self.news_client = NewsAPIClient(api_keys["news_api_key"])
        self.crawler = APNewsCrawler(api_keys["scraper_api_key"])
        self.analyzer = OpenAIArticleAnalyzer(api_keys["openai_api_key"])
        self.firestore_client = FirestoreClient(api_keys["service_account_path"])

    def process_article(self, article):
        """Process a single article through the pipeline.

        Args:
            article: The article to process.
        """
        # Crawl content
        crawled = self.crawler.crawl_article(article)

        # Analyze the article content
        analyzed = self.analyzer.analyze_article(crawled)
        pprint.pprint(analyzed)

        # Get the URL from document and encode
        encoded_url = url_to_document_id(analyzed["url"])

        # Insert document
        self.firestore_client.insert_document(
            collection=FIREBASE_COLLECTION,
            document_id=encoded_url,
            document_data=analyzed,
        )

    def run(self, total_articles: int = 5):
        """Run the news processing pipeline.

        Args:
            total_articles (int): Number of articles to process.
        """
        # Get headlines
        articles = self.news_client.get_headlines(NEWS_SOURCE, total=total_articles)

        # Process each article
        for article in tqdm(articles, desc="Processing articles"):
            try:
                self.process_article(article)
            except Exception as e:
                print(f"Failed to process article: {e}")


def load_api_keys() -> Dict[str, str]:
    """Load environment variables and return necessary API keys and credentials.

    Returns:
        Dict[str, str]: Dictionary containing all required API keys.
    """
    load_dotenv()
    return {
        "news_api_key": os.getenv("NEWS_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "scraper_api_key": os.getenv("SCRAPER_API_KEY"),
        "service_account_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    }


def main():
    """Main execution flow."""
    # Load API keys
    api_keys = load_api_keys()

    # Create and run the news processor
    processor = NewsProcessor(api_keys)
    processor.run()


if __name__ == "__main__":
    main()
