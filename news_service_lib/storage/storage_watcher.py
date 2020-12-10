"""
Abstract storage watcher module
"""
from abc import ABCMeta, abstractmethod
from typing import Any, Iterator


class StorageWatcher(metaclass=ABCMeta):
    """
    Storage watcher interface
    """

    @abstractmethod
    def consume_inserts(self) -> Iterator[Any]:
        """
        Consume the inserts in the database

        """