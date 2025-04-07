import json
from typing import Dict

import openai

from src.model import CrawledNews


def analyze_article_content(api_key: str, crawled_news: CrawledNews) -> Dict:
    """
    Analyze English news article content using ChatGPT API (function calling).
    Returns an ArticleAnalysis dataclass instance.
    """
    # Create the client
    client = openai.OpenAI(api_key=api_key)

    # Create schema for function arguments
    function_schema = {
        "name": "analyze_article",
        "description": "Analyze English news article content",
        "parameters": {
            "type": "object",
            "properties": {
                "shortened": {
                    "type": "string",
                    "description": "A concise English summary between 500 and 800 words.",
                },
                "sentences": {
                    "type": "array",
                    "description": "Each item contains two sentences: one english and one translated Vietnamese. Must cover all the sentences in the shortened version",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 2,
                    },
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "business",
                        "entertainment",
                        "general",
                        "health",
                        "science",
                        "sports",
                        "technology",
                    ],
                },
                "words": {
                    "type": "array",
                    "description": "Words/Phrases in the shortened version that are most notable, interesting, most-frequently used, or challenging. Do not include any private names/information. Eliminate any empty word from the array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "base": {
                                "type": "string",
                                "description": "Base form of the word (singular, etc...)",
                            },
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
                                    "cụm động từ",
                                ],
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
                                "maxItems": 3,
                            },
                        },
                        "required": [
                            "word",
                            "base",
                            "translation",
                            "type",
                            "usage",
                            "example",
                        ],
                    },
                    "minItems": 10,
                    "maxItems": 15,
                },
            },
            "required": ["shortened", "sentences", "category", "words"],
        },
    }

    # Create the message for chat completion
    messages = [
        {
            "role": "system",
            "content": "You analyze English news articles and return structured JSON with summary, translations, vocabulary, and category.",
        },
        {"role": "user", "content": f"Analyze this article:\n\n{crawled_news.content}"},
    ]

    # Get the response from GPT-4-turbo
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        functions=[function_schema],
        function_call={"name": "analyze_article"},
        temperature=0.7,
    )

    # Parse the arguments to JSON data and return the dictionary
    function_args = response.choices[0].message.function_call.arguments
    json_data = json.loads(function_args)
    return json_data
