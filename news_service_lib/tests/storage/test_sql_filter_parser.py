"""
SQL filter parser tests module
"""
from unittest import TestCase

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from ...storage.filter.parsers import SQLFilterParser

BASE = declarative_base()


class TestEntity(BASE):
    """
    SQLAlchemy entity for testing purposes
    """
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    test = Column(String(255), unique=True)
    test_int = Column(Integer)


class TestSQLFilterParser(TestCase):
    """
    SQL filter parser test cases implementation
    """
    def test_parse_match(self):
        """
        Test the parse match returns the binary expression with the specified key and the specified value
        """
        parsed_filters = SQLFilterParser.parse_match(TestEntity.test, 'test')
        self.assertEqual(str(parsed_filters[0]), str(TestEntity.test == 'test'))

    def test_parse_range(self):
        """
        Test the parse range with upper and lower bounds returns two binary expressions, one for the upper
        and one for the lower
        """
        test_lower = 0
        test_upper = 2
        parsed_filters = SQLFilterParser.parse_range(TestEntity.test_int, upper=test_upper, lower=test_lower)
        str_parsed_filters = [str(parsed_filter) for parsed_filter in parsed_filters]
        self.assertIn(str(TestEntity.test_int > test_lower), str_parsed_filters)
        self.assertIn(str(TestEntity.test_int < test_upper), str_parsed_filters)
