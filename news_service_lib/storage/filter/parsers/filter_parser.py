"""
Abstract filter parser module
"""
from abc import abstractmethod, ABCMeta
from typing import Any


class FilterParser(metaclass=ABCMeta):
    """
    Abstract filter parser interface
    """
    @staticmethod
    @abstractmethod
    def parse_range(key: Any, upper: Any = None, lower: Any = None) -> dict:
        """
        Parse the range filter

        Args:
            key: key of the field used to filter
            upper: Upper limit of the range filter
            lower: lower limit of the range filter

        Returns: parsed filter

        """

    @staticmethod
    @abstractmethod
    def parse_match(key: Any, value: Any) -> dict:
        """
        Parse the match filter

        Args:
            key: key of the field used to filter
            value: value to match for filtering

        Returns: parsed filter

        """
