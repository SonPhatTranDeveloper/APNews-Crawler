import json
import pprint
import openai
from src.model import ArticleAnalysis, WordItem, CrawledNews


def parse_analysis(crawled_news: CrawledNews, json_data: dict) -> ArticleAnalysis:
    words = [WordItem(**w) for w in json_data['words']]
    return ArticleAnalysis(
        article=crawled_news,
        shortened=json_data['shortened'],
        sentences=[tuple(s) for s in json_data['sentences']],
        category=json_data['category'],
        words=words
    )


def analyze_article_content(api_key: str, crawled_news: CrawledNews) -> ArticleAnalysis:
    """
    Analyze English news article content using ChatGPT API (function calling).
    Returns an ArticleAnalysis dataclass instance.
    """
    client = openai.OpenAI(api_key=api_key)

    function_schema = {
        "name": "analyze_article",
        "description": "Analyze English news article content",
        "parameters": {
            "type": "object",
            "properties": {
                "shortened": {
                    "type": "string",
                    "description": "A concise English summary between 500 and 800 words."
                },
                "sentences": {
                    "type": "array",
                    "description": "Each item contains two sentences: one english and one translated Vietnamese. Must cover all the sentences in the shortened version",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 2
                    }
                },
                "category": {
                    "type": "string",
                    "enum": ["business", "entertainment", "general", "health", "science", "sports", "technology"]
                },
                "words": {
                    "type": "array",
                    "description": "At least 10 words/phrases in the shortened version that are most notable, interesting, most-frequently used, or challenging",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "translation": {
                                "type": "string",
                                "description": "Translation of the word in Vietnamese",
                            },
                            "type": {
                                "type": "string",
                                "description": "Part of speech of the word (in Vietnamese)",
                                "enum": [
                                    "danh từ",
                                    "động từ",
                                    "tính từ",
                                    "trạng từ",
                                    "giới từ",
                                    "liên từ",
                                    "thán từ",
                                    "đại từ",
                                    "mạo từ",
                                    "cụm động từ"
                                ]
                            },
                            "usage": {
                                "type": "string",
                                "description": "Explain how to use the word (Explanation in Vietnamese)",
                            },
                            "example": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Two example sentences in English",
                                "minItems": 3,
                                "maxItems": 3
                            }
                        },
                        "required": ["word", "translation", "usage", "example"]
                    }
                }
            },
            "required": ["shortened", "sentences", "category", "words"]
        }
    }

    messages = [
        {
            "role": "system",
            "content": "You analyze English news articles and return structured JSON with summary, translations, vocabulary, and category."
        },
        {
            "role": "user",
            "content": f"Analyze this article:\n\n{crawled_news.content}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        functions=[function_schema],
        function_call={"name": "analyze_article"},
        temperature=0.7
    )

    function_args = response.choices[0].message.function_call.arguments
    json_data = json.loads(function_args)

    return parse_analysis(crawled_news, json_data)

