"""
MongoDB filter module
"""
from typing import Any

from .filter_parser import FilterParser


class MongoFilterParser(FilterParser):
    """
    MongoDB filter implementation
    """
    @staticmethod
    def parse_match(key: str, value: Any) -> dict:
        """
        Get the unique filter query with the specified value

        Args:
            key: filter query field key
            value: value to match in the query

        Returns: mongodb query

        """
        return {key: value}

    @staticmethod
    def parse_range(key: str, upper: Any = None, lower: Any = None) -> dict:
        """
        Get the range filter query with the specified limits

        Args:
            key: filter query field key
            upper: upper limit to filter
            lower: lower limit to filter

        Returns: mongodb query

        """
        range_query = {}
        if lower is not None:
            range_query['$gt'] = lower
        if upper is not None:
            range_query['$lt'] = upper
        return {key: range_query}
