"""
Base storage filter module
"""
from typing import Any

from news_service_lib.storage.filter.parsers.filter_parser import FilterParser


class Filter:
    """
    Storage filter base implementation
    """
    parser_name: str = None

    def __init__(self, key: Any, **values):
        """
        Initialize the base filter

        Args:
            key: filter key
            **values: filter values
        """
        self.key = key
        self.accepted_values = values.keys()
        for value_key, value in values.items():
            setattr(self, value_key, value)

    def __setitem__(self, key: str, value: Any):
        """
        Avoid setting values not allowed for the filter

        Args:
            key: key of the item to set
            value: value to set for the key

        """
        if not hasattr(self, key):
            raise KeyError(f'Parameter {key} not allowed for {self.__class__.__name__}')

        setattr(self, key, value)

    def __delitem__(self, key: str):
        """
        Delete the key value

        Args:
            key: key to delete value

        """
        setattr(self, key, None)

    def __eq__(self, other):
        """
        Compare two filters

        Args:
            other: filter to compare the current one

        Returns: True if the filters are equal, False otherwise

        """
        if self.key == other.key and self.accepted_values == other.accepted_values:
            for value_key in self.accepted_values:
                if not hasattr(other, value_key) or getattr(self, value_key) != getattr(other, value_key):
                    return False
            return True
        else:
            return False

    def parse_filter(self, cls: type(FilterParser)) -> Any:
        """
        Parse the current filter with the provided parser

        Args:
            cls: filter parser implementation

        Returns: parsed filter

        """
        return getattr(cls, self.parser_name)(self.key,
                                              **{value: getattr(self, value) for value in self.accepted_values})
