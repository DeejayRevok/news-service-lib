"""
New graphql model module
"""
from graphene import ObjectType, String, Boolean, List as GraphList, Float

from ..graphql_utils import CustomDateTime
from .named_entity import NamedEntity


class New(ObjectType):
    """
    New graphql model implementation
    """
    title = String(description="New title unique for all the news")
    url = String(description="New html url")
    content = String(description="New full content")
    source = String(description="New source name")
    date = CustomDateTime(description="New publish date and time")
    hydrated = Boolean(description="True if the new has been hydrated with the NLP data, false otherwise")
    entities = GraphList(NamedEntity, description='New named entities')
    summary = String(description='New content summary')
    sentiment = Float(description="New sentiment intensity")
    noun_chunk = GraphList(String, description='New noun chunks')
