"""
Match filter module
"""
from typing import Any

from news_service_lib.storage.filter.filter import Filter


class MatchFilter(Filter):
    """
    Match filter implementation
    """
    parser_name = 'parse_match'

    def __init__(self, key: Any, value: Any):
        """
        Initialize the match filter

        Args:
            key: key to match value
            value: value to match
        """
        super().__init__(key, value=value)
