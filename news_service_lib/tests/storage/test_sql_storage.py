from logging import getLogger
from unittest import TestCase

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from news_service_lib.storage.sql import SqlSessionProvider
from ...storage.implementation import SqlStorage
from ...storage.sql import create_sql_engine, SqlEngineType, init_sql_db

LOGGER = getLogger()
BASE = declarative_base()


class TestModel(BASE):
    """
    Test model
    """
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    test1 = Column(String(50))
    test2 = Column(String(50))


class TestSQLStorage(TestCase):
    """
    SQL Storage interface test cases
    """
    TEST_1 = 'test_1'
    TEST_2 = 'test_2'

    def setUp(self):
        """
        Set up test environment
        """
        test_engine = create_sql_engine(SqlEngineType.SQLITE)
        init_sql_db(BASE, test_engine)
        session_provider = SqlSessionProvider(test_engine)
        self.client = SqlStorage(session_provider, TestModel, LOGGER)

    def test_save(self):
        """
        Test if the save method persists the instance
        """
        self.client.save(TestModel(test1=self.TEST_1, test2=self.TEST_2))
        model_instances = list(self.client.get())
        self.assertIsNotNone(model_instances)
        self.assertEqual(len(model_instances), 1)
        self.assertEqual(model_instances[0].test1, self.TEST_1)
        self.assertEqual(model_instances[0].test2, self.TEST_2)

    def test_get_all(self):
        """
        Check if the get all method returns all persisted instances
        """
        self.client.save(TestModel(test1='test_11', test2='test_12'))
        self.client.save(TestModel(test1='test_21', test2='test_22'))
        model_instances = list(self.client.get())
        self.assertIsNotNone(model_instances)
        self.assertEqual(len(model_instances), 2)

    def test_get_one(self):
        """
        Check if the get one method returns the first stored instance
        """
        self.client.save(TestModel(test1=self.TEST_1, test2=self.TEST_2))
        self.client.save(TestModel(test1='test_21', test2='test_22'))
        model_instance = self.client.get_one()
        self.assertIsNotNone(model_instance)
        self.assertEqual(model_instance.test1, self.TEST_1)
        self.assertEqual(model_instance.test2, self.TEST_2)
