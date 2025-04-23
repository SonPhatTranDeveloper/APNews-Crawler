from dataclasses import dataclass
from datetime import datetime


@dataclass
class PartialArticle:
    author: str
    title: str
    url: str
    imageUrl: str


@dataclass
class FullArticle:
    article: PartialArticle
    content: str
    timestamp: int = int(datetime.now().timestamp() * 1000)
