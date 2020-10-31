import unittest
from logging import getLogger

import mongomock
from unittest.mock import patch

from ...storage.filter.match_filter import MatchFilter
from ...storage.implementation.mongo_storage import MongoStorage

LOGGER = getLogger()
MOCKED_ITEM = {'id': 1, 'test': 'test'}
MOCKED_ITEM_UPDATE = {'id': 1, 'test': 'test2'}


class TestMongoStorage(unittest.TestCase):
    MONGO_HOST = '0.1.2.3'
    MONGO_PORT = 1234
    MONGO_MEMBER = f'{MONGO_HOST}:{MONGO_PORT}'
    DATABASE = 'test'
    COLLECTION = 'test'

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    @patch.object(MongoStorage, '_init_replicaset')
    def test_collection_not_set(self, _):
        """
        Test if not setting the collection raises error
        """

        mongo_client = MongoStorage(self.MONGO_MEMBER, 'test', self.DATABASE, LOGGER)
        with self.assertRaises(AttributeError):
            mongo_client.save(MOCKED_ITEM)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    @patch.object(MongoStorage, '_init_replicaset')
    def test_save(self, _):
        """
        Test the persist functionality
        """
        mongo_client = MongoStorage(self.MONGO_MEMBER, 'test', self.DATABASE, LOGGER)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        stored_item = mongo_client.get_one()

        self.assertEqual(stored_item, MOCKED_ITEM)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    @patch.object(MongoStorage, '_init_replicaset')
    def test_get_one(self, _):
        """
        Test querying one item
        """
        mongo_client = MongoStorage(self.MONGO_MEMBER, 'test', self.DATABASE, LOGGER)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        mongo_client.save(MOCKED_ITEM_UPDATE)

        first_item = mongo_client.get_one()
        self.assertEqual(first_item, MOCKED_ITEM)

        query_item = mongo_client.get_one([MatchFilter('test', 'test2')])
        self.assertEqual(query_item, MOCKED_ITEM_UPDATE)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    @patch.object(MongoStorage, '_init_replicaset')
    def test_get(self, _):
        """
        Test querying multiple items
        """
        mongo_client = MongoStorage(self.MONGO_MEMBER, 'test', self.DATABASE, LOGGER)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        mongo_client.save(MOCKED_ITEM_UPDATE)

        items = mongo_client.get()
        self.assertEqual(list(items), [MOCKED_ITEM, MOCKED_ITEM_UPDATE])

        filtered_items = list(mongo_client.get([MatchFilter('test', 'test2')]))
        self.assertEqual(len(filtered_items), 1)
        self.assertEqual(filtered_items[0], MOCKED_ITEM_UPDATE)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    @patch.object(MongoStorage, '_init_replicaset')
    def test_delete(self, _):
        """
        Test the delete functionality
        """
        mongo_client = MongoStorage(self.MONGO_MEMBER, 'test', self.DATABASE, LOGGER)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)

        items = list(mongo_client.get())
        self.assertEqual(len(items), 1)

        mongo_client.delete(MOCKED_ITEM['_id'])
        items = list(mongo_client.get())
        self.assertEqual(len(items), 0)
