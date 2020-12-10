"""
MongoDB storage implementation module
"""
import functools
from logging import Logger
from typing import Callable, Any, Iterator, List

import pymongo
from pymongo.errors import ServerSelectionTimeoutError

from ..filter.filter import Filter
from ..filter.parsers.mongo_filter_parser import MongoFilterParser
from ..sort_direction import SortDirection
from .storage import Storage
from ..storage_watcher import StorageWatcher


def check_collection(function: Callable) -> Any:
    """
    Check if collection is configured

    Args:
        function: check before this function execution

    Returns: fn execution result

    """

    @functools.wraps(function)
    def managed(*args, **kwargs) -> Any:
        """
        Decorate the decorated function with its input args and kwargs

        Args:
            *args: decorated function execution positional arguments
            **kwargs: decorated function execution keyword arguments

        Returns: decorated function execution result

        """
        if args[0].collection is not None:
            return function(*args, **kwargs)
        else:
            raise AttributeError('Collection not set')

    return managed


class MongoStorage(Storage, StorageWatcher):
    """
    MongoDB storage implementation
    """

    def __init__(self, members: str, rsname: str, database: str, logger: Logger):
        """
        Initialize a mongo storage client

        Args:
            members: mongodb replicaset members address
            rsname: mongodb replicaset name
            database: mongodb database name
        """
        members = members.split(',')
        self._logger = logger
        self._init_replicaset(members, rsname)
        self._mongo_client = pymongo.MongoClient(members[0], replicaset=rsname, connect=True)
        self._database = self._mongo_client[database]
        self.collection = None

    def _init_replicaset(self, members: List[str], rsname: str):
        """
        Initialize the mongodb replicaset

        Args:
            members: replicaset members addresses
            rsname: replicaset name

        """
        try:
            first_host = members[0].split(':')[0]
            first_port = int(members[0].split(':')[1])
            mongo_admin_client = pymongo.MongoClient(first_host, first_port, connect=True)
            rs_config = {'_id': rsname, 'members': [{'_id': 0, 'host': members[0]}, {'_id': 1, 'host': members[1]}]}
            mongo_admin_client.admin.command("replSetInitiate", rs_config)
            mongo_admin_client.close()
        except Exception as ex:
            self._logger.info('Replicaset already initialized %s', str(ex))

    @check_collection
    def save(self, item: dict):
        """
        Persist the specified item if filters do not match

        Args:
            item: item to persist

        """
        self.collection.insert_one(item)

    @staticmethod
    def _parse_filters(filters: List[Filter]) -> dict:
        """
        Parse the given filters to a dictionary query

        Args:
            filters: filters to be parsed

        Returns: query resulting of parsing the filters

        """
        aggregated_query = {}
        if filters is not None and len(filters) > 0:
            for filter_instance in filters:
                query = filter_instance.parse_filter(MongoFilterParser)
                aggregated_query = {**aggregated_query, **query}
        return aggregated_query

    @check_collection
    def get(self, filters: List[Filter] = None,
            sort_key: str = None,
            sort_direction: SortDirection = None) -> Iterator[dict]:
        """
        Get items which match the specified filters

        Args:
            filters: filters to apply
            sort_key: key to sort the results
            sort_direction: direction of the result sorting

        Returns: iterator to the matching items

        """
        cursor = self.collection.find(self._parse_filters(filters))

        if sort_key:
            cursor = cursor.sort(sort_key, sort_direction.value[0])

        for item in cursor:
            yield item

    @check_collection
    def get_one(self, filters: List[Filter] = None) -> dict:
        """
        Get first queried item

        Args:
            filters: filters to apply

        Returns: persisted item matching filters

        """
        return self.collection.find_one(self._parse_filters(filters))

    @check_collection
    def delete(self, identifier: str):
        """
        Delete the identified item

        Args:
            identifier: identifier of the item

        """
        self.collection.remove(identifier)

    @check_collection
    def consume_inserts(self) -> Iterator[dict]:
        """
        Consume the insert operations

        """
        insert_consumer = self.collection.watch([{'$match': {'operationType': 'insert'}}])
        try:
            for insert_change in insert_consumer:
                yield insert_change['fullDocument']
        except Exception as ex:
            insert_consumer.close()
            raise ex
        except KeyboardInterrupt as kex:
            insert_consumer.close()
            raise kex

    def set_collection(self, collection: str):
        """
        Set collection used by the implementation

        Args:
            collection: collection to use

        """
        self.collection = self._database[collection]
