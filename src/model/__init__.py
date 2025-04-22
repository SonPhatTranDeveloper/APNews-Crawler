from dataclasses import dataclass


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
