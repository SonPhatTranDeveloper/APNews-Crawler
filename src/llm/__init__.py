import json
from typing import Dict

import openai

from constants import OPENAI_MODEL, OPENAI_TEMP
from src.model import CrawledNews


def analyze_article_content(
    crawled_news: CrawledNews,
    api_key: str,
) -> Dict:
    """
    Analyze English news article content using ChatGPT API (function calling).
    Returns an ArticleAnalysis dataclass instance.
    """
    # Create the client
    client = openai.OpenAI(api_key=api_key)

    # Create schema for function arguments
    function_schema = {
        "name": "analyze_article",
        "description": "Analyze English news article content. Make sure you escape things properly so that return JSON arguments is valid.",
        "parameters": {
            "type": "object",
            "properties": {
                "shortened": {
                    "type": "string",
                    "description": (
                        "A concise English summary between 500 and 800 words.\n\n"
                        "Rewrite the article in a more engaging, concise, and human-readable style. "
                        "Avoid generic academic phrasing like 'The article discusses...' or 'It highlights...'. "
                        "Instead, get straight to the point, use active voice, and bring out the key points clearly, "
                        "as if you're explaining it to a curious friend or writing for a newsletter.\n\n"
                        "Avoid:\n"
                        "- Passive voice\n"
                        "- Overused phrases like 'The article states', 'It concludes'\n"
                        "- Dense paragraph summaries\n\n"
                    ),
                },
                "sentences": {
                    "type": "array",
                    "description": "Each item is an object with the English sentence and its Vietnamese translation. Must cover all the sentences in the shortened version. Do not include any weird symbols or emojis.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_sentence": {
                                "type": "string",
                                "description": "Sentence in English",
                            },
                            "translated_sentence": {
                                "type": "string",
                                "description": "Sentence translated to Vietnamese",
                            },
                        },
                        "required": ["original_sentence", "translated_sentence"],
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
                    "description": "MUST INCLUDE At least 15 words/phrases in the shortened version that are most notable, interesting, most-frequently used, or challenging. Eliminate any empty word from the array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {
                                "type": "string",
                                "description": "Make sure that the word is in the EXACT same form as it appears in the shortened version. DO NOT change the form of the word. DO NOT choose words which are private names/information. ",
                            },
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
                                "description": (
                                    "Longest explaination of how to use the word. "
                                    "DO NOT INCLUDE examples in this section. "
                                    "MUST BE in Vietnamese. "
                                    "PLEASE DO NOT write this in English. "
                                    "DO NOT START WITH the word itself."
                                ),
                            },
                            "example": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "MUST INCLUDE THREE (3) example sentences in English",
                                "minItems": 3,
                            },
                        },
                        "required": [
                            "word",
                            "base",
                            "usage",
                            "type",
                            "meaning",
                            "example",
                        ],
                    },
                    "minItems": 15,
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
        model=OPENAI_MODEL,
        messages=messages,
        functions=[function_schema],
        function_call={"name": "analyze_article"},
        temperature=OPENAI_TEMP,
    )

    # Parse the arguments to JSON data and return the dictionary
    function_args = response.choices[0].message.function_call.arguments
    analysis_result = json.loads(function_args)

    # Add metadata
    article = crawled_news.article
    analysis_result.update(
        {
            "url": article.url,
            "title": article.title,
            "author": article.author,
            "imageUrl": article.imageUrl,
        }
    )

    return analysis_result
