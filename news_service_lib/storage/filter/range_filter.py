"""
Range filter module
"""
from typing import Any

from news_service_lib.storage.filter.filter import Filter


class RangeFilter(Filter):
    """
    Range filter implementation
    """
    parser_name = 'parse_range'

    def __init__(self, key: Any, lower: Any = None, upper: Any = None):
        """
        Initialize the range filter

        Args:
            key: filtering key
            lower: lower bound to filter
            upper: upper bound to filter
        """
        super().__init__(key, lower=lower, upper=upper)
