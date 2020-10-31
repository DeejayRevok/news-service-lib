"""
SQL filter module
"""
from typing import List, Any

from sqlalchemy import Column
from sqlalchemy.sql.elements import BinaryExpression

from .filter_parser import FilterParser


class SQLFilterParser(FilterParser):
    """
    SQL filter implementation
    """

    @staticmethod
    def parse_match(key: Column, value: Any) -> List[BinaryExpression]:
        """
        Get the unique filter query with the specified value

        Args:
            key: filter query field key
            value: value to match in the query

        Returns: SQL binary expression

        """
        return [key == value]

    @staticmethod
    def parse_range(key: Column, upper: Any = None, lower: Any = None) -> List[BinaryExpression]:
        """
        Get the range filter query with the specified limits

        Args:
            key: filter query field key
            upper: upper limit to filter
            lower: lower limit to filter

        Returns: SQL query

        """
        expressions = list()
        if lower:
            expressions.append(key > lower)
        if upper:
            expressions.append(key < upper)
        return expressions
