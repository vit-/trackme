from dataclasses import dataclass

from elasticsearch import Elasticsearch


@dataclass()
class Config:
    auth_token: str
    es: Elasticsearch
