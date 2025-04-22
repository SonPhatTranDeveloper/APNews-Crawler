import json
from typing import Dict

import openai

from constants import OPENAI_MODEL, OPENAI_TEMP
from .base_analyzer import BaseArticleAnalyzer

from abc import ABC, abstractmethod
from typing import Dict

from src.model import FullArticle


class BaseArticleAnalyzer(ABC):
    """Abstract base class for article analysis using LLMs."""

    @abstractmethod
    def analyze_article(self, article: FullArticle) -> Dict:
        """Analyze an article using LLM.

        Args:
            article (FullArticle): The article to analyze.

        Returns:
            Dict: Analysis results including summary, translations, vocabulary, and quiz.
        """
        pass


class OpenAIArticleAnalyzer(BaseArticleAnalyzer):
    """OpenAI implementation of the article analyzer."""

    def __init__(self, api_key: str):
        """Initialize the OpenAI analyzer.

        Args:
            api_key (str): OpenAI API key.
        """
        self.client = openai.OpenAI(api_key=api_key)

    def _get_step1_function_schema(self) -> Dict:
        """Get the function schema for step 1 (summary and translation).

        Returns:
            Dict: Function schema for OpenAI API.
        """
        return {
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

    def _get_step2_function_schema(self) -> Dict:
        """Get the function schema for step 2 (vocabulary and quiz).

        Returns:
            Dict: Function schema for OpenAI API.
        """
        return {
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
                    "required": ["word", "base"],
                }
            },
        }

    def _analyze_step1(self, content: str) -> Dict:
        """Perform step 1 analysis (summary and translation).

        Args:
            content (str): Article content to analyze.

        Returns:
            Dict: Analysis results from step 1.
        """
        prompt = [
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
                "content": f"Summarize and translate this article:\n\n{content}",
            },
        ]

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt,
            functions=[self._get_step1_function_schema()],
            function_call={"name": "summarize_and_translate_article"},
            temperature=OPENAI_TEMP,
        )

        return json.loads(response.choices[0].message.function_call.arguments)

    def _analyze_step2(self, shortened: str) -> Dict:
        """Perform step 2 analysis (vocabulary and quiz).

        Args:
            shortened (str): Shortened version of the article.

        Returns:
            Dict: Analysis results from step 2.
        """
        prompt = [
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

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt,
            functions=[self._get_step2_function_schema()],
            function_call={"name": "extract_vocabulary"},
            temperature=OPENAI_TEMP,
        )

        return json.loads(response.choices[0].message.function_call.arguments)

    def analyze_article(self, article: FullArticle) -> Dict:
        """Analyze an article using OpenAI.

        Args:
            article (FullArticle): The article to analyze.

        Returns:
            Dict: Analysis results including summary, translations, vocabulary, and quiz.
        """
        # Step 1: Generate shortened version, category, difficulty, and translations
        step1_data = self._analyze_step1(article.content[0])

        # Step 2: Extract vocabulary and generate quiz
        step2_data = self._analyze_step2(step1_data["shortened"])

        # Merge all data
        analysis_result = {
            **step1_data,
            **step2_data,
            "url": article.article.url,
            "title": article.article.title,
            "author": article.article.author,
            "imageUrl": article.article.imageUrl,
        }

        return analysis_result 