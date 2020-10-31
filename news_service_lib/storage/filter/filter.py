"""Base storage filter module"""
from typing import Any

from news_service_lib.storage.filter.parsers.filter_parser import FilterParser


class Filter:
    """Storage filter base implementation"""
    parser_name: str = None

    def __init__(self, key: Any, **values):
        self.key = key
        self.accepted_values = values.keys()
        for value_key, value in values.items():
            setattr(self, value_key, value)

    def __setitem__(self, key: str, value: Any):
        if not hasattr(self, key):
            raise KeyError(f'Parameter {key} not allowed for {self.__class__.__name__}')

        setattr(self, key, value)

    def __delitem__(self, key: str):
        setattr(self, key, None)

    def __eq__(self, other):
        if self.key == other.key and self.accepted_values == other.accepted_values:
            for value_key in self.accepted_values:
                if not hasattr(other, value_key) or getattr(self, value_key) != getattr(other, value_key):
                    return False
            return True
        else:
            return False

    def parse_filter(self, cls: type(FilterParser)) -> Any:
        return getattr(cls, self.parser_name)(self.key,
                                              **{value: getattr(self, value) for value in self.accepted_values})
