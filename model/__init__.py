from dataclasses import dataclass


@dataclass
class InitialNews:
    author: str
    title: str
    url: str