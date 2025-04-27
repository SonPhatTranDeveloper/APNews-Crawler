import os
from typing import Dict

from dotenv import load_dotenv

from constants import VIETNAMESE_NEWS_SOURCE, NEWS_SOURCE
from src.processor import VietnameseNewsProcessorFactory, DefaultNewsProcessorFactory


def load_api_keys_news_api() -> Dict[str, str]:
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


def load_api_keys_news_io_api() -> Dict[str, str]:
    """Load environment variables and return necessary API keys and credentials.

    Returns:
        Dict[str, str]: Dictionary containing all required API keys.
    """
    load_dotenv()
    return {
        "news_io_api_key": os.getenv("NEWS_IO_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "scraper_api_key": os.getenv("SCRAPER_API_KEY"),
        "service_account_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    }


def main():
    """Main execution flow."""
    # Load API keys
    api_keys = load_api_keys_news_api()

    # Create factory and get processor
    factory = DefaultNewsProcessorFactory(api_keys)
    processor = factory.create_processor()

    # Run the processor
    processor.run(source_id=NEWS_SOURCE, total_articles=1)


if __name__ == "__main__":
    main()
