from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class InitialNews:
    author: str
    title: str
    url: str


@dataclass
class CrawledNews:
    article: InitialNews
    content: str


@dataclass
class WordItem:
    word: str
    translation: str
    type: str
    usage: str
    example: List[str]


@dataclass
class ArticleAnalysis:
    article: InitialNews
    shortened: str
    sentences: List[Tuple[str, str]]  # (English, Vietnamese)
    category: str
    words: List[WordItem]