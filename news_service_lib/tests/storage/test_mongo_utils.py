"""
Mongo utils tests module
"""
from unittest import TestCase

import mongomock
import pymongo

from ...storage.mongo_utils import mongo_health_check


class TestMongoUtils(TestCase):
    """
    Mongo utils test cases implementation
    """
    MONGO_HOST = '0.1.2.3'
    MONGO_PORT = 1234

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_healthcheck_success(self):
        """
        Test when the mongodb is available healthcheck returns true
        """

        mongo_client =pymongo.MongoClient(host=self.MONGO_HOST, port=self.MONGO_PORT)
        self.assertTrue(mongo_health_check(mongo_client))

    def test_healthcheck_fail(self):
        """
        Test when mongodb is not available healthcheck returns false
        """

        mongo_client = pymongo.MongoClient(host=self.MONGO_HOST, port=self.MONGO_PORT)
        self.assertFalse(mongo_health_check(mongo_client))
