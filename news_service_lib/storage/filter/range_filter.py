from typing import Any

from news_service_lib.storage.filter.filter import Filter


class RangeFilter(Filter):

    parser_name = 'parse_range'

    def __init__(self, key: Any, lower: Any = None, upper: Any = None):
        super().__init__(key, lower=lower, upper=upper)
