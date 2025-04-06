from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class InitialNews:
    author: str
    title: str
    url: str


@dataclass
class NotableWord:
    word_or_phrase: str
    meaning: str
    usage: str
    example: str


@dataclass
class CrawledNews:
    article: InitialNews
    content: str


@dataclass
class TranslatedNews:
    article: InitialNews
    category: str
    content: List[Tuple[str, str]]
    notable_words: List[NotableWord]