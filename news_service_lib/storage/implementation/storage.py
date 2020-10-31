"""
Abstract storage module
"""
from abc import ABCMeta, abstractmethod
from typing import Iterator, List, Any

from ..filter.filter import Filter
from ..sort_direction import SortDirection


class Storage(metaclass=ABCMeta):
    """
    Storage interface
    """

    @abstractmethod
    def save(self, item: Any):
        """
        Persist the specified item

        Args:
            item: item to persist

        """

    @abstractmethod
    def get(self, filters: List[Filter] = None,
            sort_key: str = None,
            sort_direction: SortDirection = None) -> Iterator[Any]:
        """
        Get items from the storage. If filters are provided filter results.

        Args:
            filters: filters to apply
            sort_key: key to sort the results
            sort_direction: direction of the result sorting

        Returns: iterator to dictionary representation of the items

        """

    @abstractmethod
    def get_one(self, filters: List[Filter] = None) -> Any:
        """
        Get a unique storage item which matches the filters if provided

        Args:
            filters: filters to apply

        Returns: persisted item matching filters

        """

    @abstractmethod
    def delete(self, identifier: Any):
        """
        Delete the specified stored item

        Args:
            identifier: identifier of the item to delete

        """
