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
    Two-step analysis of English news article using ChatGPT API:
    Step 1 - Generate shortened version, category, difficulty and translated sentences
    Step 2 - Extract and categorize vocabulary from shortened text
    Returns full enriched article data.
    """
    client = openai.OpenAI(api_key=api_key)

    # STEP 1: Function schema for summary, category, difficulty, and translation
    step1_function_schema = {
        "name": "summarize_and_translate_article",
        "description": "Summarizes the article into a shortened version, categorizes it, estimates difficulty, and provides sentence-level English-Vietnamese translations.",
        "parameters": {
            "type": "object",
            "properties": {
                "shortened": {
                    "type": "string",
                    "description": "The rewritten article in 200-400 words, simplified, engaging, and natural.",
                },
                "sentences": {
                    "type": "array",
                    "description": "List of translated sentences",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_sentence": {"type": "string"},
                            "translated_sentence": {"type": "string"},
                        },
                        "required": ["original_sentence", "translated_sentence"],
                    },
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "Kinh tế",
                        "Chính trị",
                        "Giải trí",
                        "Tin chung",
                        "Sức khoẻ",
                        "Khoa học",
                        "Thể thao",
                        "Công nghệ",
                    ],
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["Dễ", "Trung bình", "Thử thách"],
                },
            },
            "required": ["shortened", "sentences", "category", "difficulty"],
        },
    }

    step1_prompt = [
        {
            "role": "system",
            "content": (
                "You are an assistant that summarizes English articles and translates each sentence into Vietnamese.\n"
                "Return a JSON object with: 'shortened', 'sentences', 'category', and 'difficulty'.\n"
                "The 'shortened' must be 200-400 words, human-readable, and engaging.\n"
                "Each sentence in the shortened version must have its English-Vietnamese pair in 'sentences'.\n"
                "Also classify the article's category and estimate its difficulty for English learners."
            ),
        },
        {
            "role": "user",
            "content": f"Summarize and translate this article:\n\n{crawled_news.content}",
        },
    ]

    step1_response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=step1_prompt,
        functions=[step1_function_schema],
        function_call={"name": "summarize_and_translate_article"},
        temperature=OPENAI_TEMP,
    )

    step1_data = json.loads(step1_response.choices[0].message.function_call.arguments)
    shortened = step1_data["shortened"]

    # STEP 2: Function schema for vocabulary analysis and bilingual quiz generation
    step2_function_schema = {
        "name": "extract_vocabulary",
        "description": (
            "Extracts vocabulary that appears in the shortened version and categorizes them by difficulty. "
            "Also generates a 3-question multiple choice quiz (with each option having both English and Vietnamese)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "easy_words": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 7,
                    "description": 'Words from the shortened version that are simple and beginner-friendly.',
                    "items": {"$ref": "#/definitions/word"},
                },
                "medium_words": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 7,
                    "description": 'Intermediate words from the shortened version.',
                    "items": {"$ref": "#/definitions/word"},
                },
                "hard_words": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 7,
                    "description": 'Advanced or challenging words from the shortened version.',
                    "items": {"$ref": "#/definitions/word"},
                },
                "quiz": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Multiple-choice quiz to test understanding, with bilingual options",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "object",
                                "properties": {
                                    "en": {"type": "string"},
                                    "vi": {"type": "string"},
                                },
                                "required": ["en", "vi"],
                            },
                            "options": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 3,
                                "description": "Four answer choices, each with English and Vietnamese text",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "en": {"type": "string"},
                                        "vi": {"type": "string"},
                                    },
                                    "required": ["en", "vi"],
                                },
                            },
                            "correct_answer": {
                                "type": "object",
                                "properties": {
                                    "en": {
                                        "type": "string",
                                        "description": "Must match one of the option.en values",
                                    },
                                    "vi": {
                                        "type": "string",
                                        "description": "Must match one of the option.vi values",
                                    },
                                },
                                "required": ["en", "vi"],
                            },
                        },
                        "required": ["question", "options", "correct_answer"],
                    },
                },
            },
            "required": ["easy_words", "medium_words", "hard_words", "quiz"],
        },
        "definitions": {
            "word": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "base": {"type": "string"},
                },
                "required": [
                    "word",
                    "base",
                ],
            }
        },
    }

    step2_prompt = [
        {
            "role": "system",
            "content": (
                "You extract vocabulary that appears EXACTLY in the input text and group it by difficulty.\n"
                "Return JSON with 'easy_words', 'medium_words', and 'hard_words', each containing 15+ words.\n"
                "Each word must include: word, base (its base form)\n"
                "Then generate a 3-question multiple choice quiz to test reading comprehension of the shortened version.\n"
                "Each quiz entry must include:\n"
                "- question: {en: English version, vi: Vietnamese translation}\n"
                "- options: array of 4 choices, each like {en: ..., vi: ...}\n"
                "- correct_answer: {en: correct English choice, vi: correct Vietnamese translation (must match one of the options)}\n"
                "Remember to specifically INCLUDE THE QUIZ - NEVER OMIT THE QUIZ\n"
                "Remember to specifically INCLUDE THE EXAMPLES - NEVER OMIT THE EXAMPLES.\n\n"
                "Do NOT invent vocabulary or quiz questions not based directly on the shortened version."
            ),
        },
        {
            "role": "user",
            "content": f"Analyze vocabulary and generate a bilingual quiz from this shortened version:\n\n{shortened}",
        },
    ]

    step2_response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=step2_prompt,
        functions=[step2_function_schema],
        function_call={"name": "extract_vocabulary"},
        temperature=OPENAI_TEMP,
    )

    step2_data = json.loads(step2_response.choices[0].message.function_call.arguments)

    # Merge all data
    analysis_result = {
        **step1_data,
        **step2_data,
        "url": crawled_news.article.url,
        "title": crawled_news.article.title,
        "author": crawled_news.article.author,
        "imageUrl": crawled_news.article.imageUrl,
    }

    return analysis_result
