"""
Factories tests module
"""
import unittest
from logging import getLogger

from ...storage.implementation.mongo_storage import MongoStorage
from ...storage import storage_factory

LOGGER = getLogger()


class TestFactories(unittest.TestCase):
    """
    Factories test cases
    """
    def test_storage_factory_unknown(self):
        """
        Test storage factory raises error for unknown type
        """
        with self.assertRaises(NotImplementedError):
            storage_factory('UNKNOWN', {}, LOGGER)

    def test_storage_factory_mongo(self):
        """
        Test storage factory with Mongo type creates Mongo client
        """
        storage = storage_factory('MONGO', {'members': '0.0.0.0:1234', 'rsname': 'test', 'database': 'test'}, LOGGER)
        self.assertTrue(isinstance(storage, MongoStorage))


if __name__ == '__main__':
    unittest.main()
