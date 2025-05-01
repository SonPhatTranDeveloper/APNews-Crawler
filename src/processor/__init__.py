import pprint
import random
from abc import ABC, abstractmethod
from typing import Dict, List

from tqdm import tqdm

from constants import FIREBASE_COLLECTION, NEWS_SOURCE
from src.firebase import BaseFirebaseClient, FirestoreClient
from src.firebase.fcm_client import FCMClient
from src.llm import (
    BaseArticleAnalyzer,
    OpenAIArticleAnalyzer,
    VietnameseOpenAIArticleAnalyzer,
)
from src.model import FullArticle
from src.service import BaseNewsService, DefaultNewsService, VietnameseNewsService
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
            scraper_api_key=self.api_keys["scraper_api_key"],
        )
        analyzer = OpenAIArticleAnalyzer(self.api_keys["openai_api_key"])
        firestore_client = FirestoreClient(self.api_keys["service_account_path"])
        fcm_client = FCMClient(self.api_keys["service_account_path"])

        return NewsProcessor(
            news_service=news_service,
            analyzer=analyzer,
            firestore_client=firestore_client,
            fcm_client=fcm_client,
        )


class VietnameseNewsProcessorFactory(BaseNewsProcessorFactory):
    """Factory for creating NewsProcessors with Vietnamese-specific implementations."""

    def create_processor(self) -> "NewsProcessor":
        """Create a NewsProcessor with Vietnamese-specific implementations.

        Returns:
            NewsProcessor: A processor with Vietnamese implementations.
        """
        news_service = VietnameseNewsService(
            news_io_api_key=self.api_keys["news_io_api_key"],
            scraper_api_key=self.api_keys["scraper_api_key"],
        )
        analyzer = VietnameseOpenAIArticleAnalyzer(self.api_keys["openai_api_key"])
        firestore_client = FirestoreClient(self.api_keys["service_account_path"])
        fcm_client = FCMClient(self.api_keys["service_account_path"])

        return NewsProcessor(
            news_service=news_service,
            analyzer=analyzer,
            firestore_client=firestore_client,
            fcm_client=fcm_client,
        )


class NewsProcessor:
    """Class to handle the news processing pipeline."""

    def __init__(
        self,
        news_service: BaseNewsService,
        analyzer: BaseArticleAnalyzer,
        firestore_client: BaseFirebaseClient,
        fcm_client: FCMClient,
    ):
        """Initialize the news processor with its components.

        Args:
            news_service (BaseNewsService): Service for fetching and crawling articles
            analyzer (BaseArticleAnalyzer): Analyzer for processing article content
            firestore_client (BaseFirebaseClient): Client for storing processed articles
            fcm_client (FCMClient): Client for sending push notifications
        """
        self.news_service = news_service
        self.analyzer = analyzer
        self.firestore_client = firestore_client
        self.fcm_client = fcm_client

    def process_article(self, article: FullArticle) -> Dict:
        """Process a single article through the pipeline.

        Args:
            article: The article to process.

        Returns:
            Dict: The analyzed article data.
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

        return analyzed

    def run(self, source_id: str, total_articles: int = 10):
        """Run the news processing pipeline.

        Args:
            total_articles (int): Number of articles to process.
        """
        # Get full articles including content
        articles = self.news_service.get_full_articles(source_id, total=total_articles)

        # Process each article and store analyzed results
        processed_articles = []
        for article in tqdm(articles, desc="Processing articles"):
            try:
                analyzed = self.process_article(article)
                processed_articles.append(analyzed)
            except Exception as e:
                print(f"Failed to process article: {e}")

        # If we have processed articles, announce a random one
        if processed_articles:
            try:
                # Choose the latest article
                latest_article = processed_articles[-1]

                # Send push notification for the random article
                self.fcm_client.send_to_topic(
                    topic="news_channel",
                    title="Ụm bò... Tin tiếng anh nóng hổi",
                    body=latest_article["title"],
                )
            except Exception as e:
                print(f"Failed to send featured article notification: {e}")
