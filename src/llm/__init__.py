import json
from typing import Dict

import openai

from constants import OPENAI_MODEL, OPENAI_TEMP
from src.model import FullArticle
from .openai_analyzer import OpenAIArticleAnalyzer


def analyze_article_content(
    article: FullArticle,
    api_key: str,
) -> Dict:
    """Legacy function that uses OpenAIArticleAnalyzer internally.
    
    Args:
        article (FullArticle): The article to analyze.
        api_key (str): OpenAI API key.
        
    Returns:
        Dict: Analysis results including summary, translations, vocabulary, and quiz.
    """
    analyzer = OpenAIArticleAnalyzer(api_key)
    return analyzer.analyze_article(article)
