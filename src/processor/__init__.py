import pprint
from abc import ABC, abstractmethod
from typing import Dict, Type

from tqdm import tqdm

from constants import FIREBASE_COLLECTION, NEWS_SOURCE
from src.firebase import BaseFirebaseClient, FirestoreClient
from src.llm import BaseArticleAnalyzer, OpenAIArticleAnalyzer
from src.service import BaseNewsService, DefaultNewsService
from src.utils import url_to_document_id


class BaseNewsProcessorFactory(ABC):
    """Abstract base class for NewsProcessor factories."""

    def __init__(self, api_keys: Dict[str, str]):
        """Initialize the factory with API keys.

        Args:
            api_keys (Dict[str, str]): Dictionary containing all required API keys.
        """
        self.api_keys = api_keys

    @abstractmethod
    def create_processor(self) -> "NewsProcessor":
        """Create a NewsProcessor instance.

        Returns:
            NewsProcessor: A configured processor instance.
        """
        pass


class DefaultNewsProcessorFactory(BaseNewsProcessorFactory):
    """Factory for creating NewsProcessors with default implementations."""

    def create_processor(self) -> "NewsProcessor":
        """Create a NewsProcessor with default implementations.

        Returns:
            NewsProcessor: A processor with default implementations.
        """
        news_service = DefaultNewsService(
            news_api_key=self.api_keys["news_api_key"],
            scraper_api_key=self.api_keys["scraper_api_key"]
        )
        analyzer = OpenAIArticleAnalyzer(self.api_keys["openai_api_key"])
        firestore_client = FirestoreClient(self.api_keys["service_account_path"])

        return NewsProcessor(
            news_service=news_service,
            analyzer=analyzer,
            firestore_client=firestore_client,
        )


class NewsProcessor:
    """Class to handle the news processing pipeline."""

    def __init__(
        self,
        news_service: BaseNewsService,
        analyzer: BaseArticleAnalyzer,
        firestore_client: BaseFirebaseClient,
    ):
        """Initialize the news processor with its components.

        Args:
            news_service (BaseNewsService): Service for fetching and crawling articles
            analyzer (BaseArticleAnalyzer): Analyzer for processing article content
            firestore_client (BaseFirebaseClient): Client for storing processed articles
        """
        self.news_service = news_service
        self.analyzer = analyzer
        self.firestore_client = firestore_client

    def process_article(self, article):
        """Process a single article through the pipeline.

        Args:
            article: The article to process.
        """
        # Analyze the article content
        analyzed = self.analyzer.analyze_article(article)
        pprint.pprint(analyzed)

        # Get the URL from document and encode
        encoded_url = url_to_document_id(analyzed["url"])

        # Insert document
        self.firestore_client.insert_document(
            collection=FIREBASE_COLLECTION,
            document_id=encoded_url,
            document_data=analyzed,
        )

    def run(self, total_articles: int = 10):
        """Run the news processing pipeline.

        Args:
            total_articles (int): Number of articles to process.
        """
        # Get full articles including content
        articles = self.news_service.get_full_articles(NEWS_SOURCE, total=total_articles)

        # Process each article
        for article in tqdm(articles, desc="Processing articles"):
            try:
                self.process_article(article)
            except Exception as e:
                print(f"Failed to process article: {e}")
