from src.model import FullArticle, PartialArticle
from .ap_news_crawler import APNewsCrawler


# For backward compatibility
def crawl_ap_article(news: PartialArticle, api_key: str) -> FullArticle:
    """Legacy function that uses APNewsCrawler internally.

    Args:
        news (PartialArticle): The initial news metadata with URL.
        api_key (str): ScraperAPI key.

    Returns:
        FullArticle: A structured result with metadata and article content.
    """
    crawler = APNewsCrawler(api_key)
    return crawler.crawl_article(news)
