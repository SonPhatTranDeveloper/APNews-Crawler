import pprint
from abc import ABC, abstractmethod
from typing import Dict, Type

from tqdm import tqdm

from constants import FIREBASE_COLLECTION, NEWS_SOURCE
from src.crawler import APNewsCrawler, BaseNewsCrawler
from src.firebase import BaseFirebaseClient, FirestoreClient
from src.llm import BaseArticleAnalyzer, OpenAIArticleAnalyzer
from src.news import BaseNewsClient, NewsAPIClient
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
        news_client = NewsAPIClient(self.api_keys["news_api_key"])
        crawler = APNewsCrawler(self.api_keys["scraper_api_key"])
        analyzer = OpenAIArticleAnalyzer(self.api_keys["openai_api_key"])
        firestore_client = FirestoreClient(self.api_keys["service_account_path"])

        return NewsProcessor(
            news_client=news_client,
            crawler=crawler,
            analyzer=analyzer,
            firestore_client=firestore_client,
        )


class CustomNewsProcessorFactory(BaseNewsProcessorFactory):
    """Factory for creating NewsProcessors with custom implementations."""

    def __init__(
        self,
        api_keys: Dict[str, str],
        news_client_class: Type[BaseNewsClient] = NewsAPIClient,
        crawler_class: Type[BaseNewsCrawler] = APNewsCrawler,
        analyzer_class: Type[BaseArticleAnalyzer] = OpenAIArticleAnalyzer,
        firestore_client_class: Type[BaseFirebaseClient] = FirestoreClient,
        **kwargs,
    ):
        """Initialize the factory with custom implementations.

        Args:
            api_keys (Dict[str, str]): Dictionary containing all required API keys.
            news_client_class (Type[BaseNewsClient]): Class for news client implementation.
            crawler_class (Type[BaseNewsCrawler]): Class for crawler implementation.
            analyzer_class (Type[BaseArticleAnalyzer]): Class for analyzer implementation.
            firestore_client_class (Type[BaseFirebaseClient]): Class for firestore client implementation.
            **kwargs: Additional arguments to pass to the component constructors.
        """
        super().__init__(api_keys)
        self.news_client_class = news_client_class
        self.crawler_class = crawler_class
        self.analyzer_class = analyzer_class
        self.firestore_client_class = firestore_client_class
        self.kwargs = kwargs

    def create_processor(self) -> "NewsProcessor":
        """Create a NewsProcessor with custom implementations.

        Returns:
            NewsProcessor: A processor with custom implementations.
        """
        news_client = self.news_client_class(
            self.api_keys["news_api_key"], **self.kwargs.get("news_client_kwargs", {})
        )
        crawler = self.crawler_class(
            self.api_keys["scraper_api_key"], **self.kwargs.get("crawler_kwargs", {})
        )
        analyzer = self.analyzer_class(
            self.api_keys["openai_api_key"], **self.kwargs.get("analyzer_kwargs", {})
        )
        firestore_client = self.firestore_client_class(
            self.api_keys["service_account_path"],
            **self.kwargs.get("firestore_client_kwargs", {}),
        )

        return NewsProcessor(
            news_client=news_client,
            crawler=crawler,
            analyzer=analyzer,
            firestore_client=firestore_client,
        )


class MockNewsProcessorFactory(BaseNewsProcessorFactory):
    """Factory for creating NewsProcessors with mock implementations for testing."""

    def create_processor(self) -> "NewsProcessor":
        """Create a NewsProcessor with mock implementations.

        Returns:
            NewsProcessor: A processor with mock implementations.
        """
        from unittest.mock import Mock

        news_client = Mock(spec=BaseNewsClient)
        crawler = Mock(spec=BaseNewsCrawler)
        analyzer = Mock(spec=BaseArticleAnalyzer)
        firestore_client = Mock(spec=BaseFirebaseClient)

        return NewsProcessor(
            news_client=news_client,
            crawler=crawler,
            analyzer=analyzer,
            firestore_client=firestore_client,
        )


class NewsProcessor:
    """Class to handle the news processing pipeline."""

    def __init__(
        self,
        news_client: BaseNewsClient,
        crawler: BaseNewsCrawler,
        analyzer: BaseArticleAnalyzer,
        firestore_client: BaseFirebaseClient,
    ):
        """Initialize the news processor with its components.

        Args:
            news_client (BaseNewsClient): Client for fetching news articles
            crawler (BaseNewsCrawler): Crawler for extracting article content
            analyzer (BaseArticleAnalyzer): Analyzer for processing article content
            firestore_client (BaseFirebaseClient): Client for storing processed articles
        """
        self.news_client = news_client
        self.crawler = crawler
        self.analyzer = analyzer
        self.firestore_client = firestore_client

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

    def run(self, total_articles: int = 10):
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
