"""
SQL utils tests module
"""
from unittest import TestCase

from sqlalchemy import Column, Integer, inspect, String
from sqlalchemy.ext.declarative import declarative_base

from news_service_lib.storage.sql import create_sql_engine, SqlEngineType, init_sql_db, sql_health_check

BASE = declarative_base()


class TestEntity(BASE):
    """
    SQLAlchemy entity for testing purposes
    """
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    test = Column(String(255), unique=True)
    test_int = Column(Integer)


class TestSQLUtils(TestCase):
    """
    SQL utils test cases implementation
    """
    test_user = 'test_user'
    test_password = 'test_password'
    test_host = 'test_host'
    test_database = 'test_database'
    test_port = 1234

    @staticmethod
    def _set_up():
        """
        Set up test environment
        """
        return create_sql_engine(SqlEngineType.SQLITE)

    def test_create_mysql_engine(self):
        """
        Test creating the engine creates the engine with the specified type and the specified parameters
        """
        engine = create_sql_engine(SqlEngineType.MYSQL, user=self.test_user, password=self.test_password,
                                   host=self.test_host,
                                   port=self.test_port,
                                   database=self.test_database)
        self.assertEqual(str(engine.url),
                         SqlEngineType.MYSQL.uri.format(user=self.test_user, password=self.test_password,
                                                        host=self.test_host,
                                                        port=self.test_port,
                                                        database=self.test_database))

    def test_init_sql_db(self):
        """
        Test initializing the db creates the tables defined in the base schema
        """
        engine = self._set_up()
        init_sql_db(BASE, engine)
        inspector = inspect(engine)
        schemas = inspector.get_schema_names()

        tables = inspector.get_table_names(schema=schemas[0])
        self.assertEqual(tables[0], 'test')

    def test_healthcheck_success(self):
        """
        Test the healthcheck successfull returns True
        """
        engine = self._set_up()
        self.assertTrue(sql_health_check(engine))

    def test_healthcheck_fail(self):
        """
        Test the healthcheck failed returns False
        """
        engine = create_sql_engine(SqlEngineType.MYSQL,
                                   user=self.test_user,
                                   password=self.test_password,
                                   host=self.test_host,
                                   port=self.test_port,
                                   database=self.test_database)
        self.assertFalse(sql_health_check(engine))
