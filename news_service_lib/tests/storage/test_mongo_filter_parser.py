"""
Mongo filter parser tests module
"""
from unittest import TestCase

from ...storage.filter.parsers import MongoFilterParser


class TestMongoFilterParser(TestCase):
    """
    Mongo filter parser test cases implementation
    """
    def test_parse_match(self):
        """
        Test the parse match returns the dictionary with the specified key and the specified value
        """
        parsed_filter = MongoFilterParser.parse_match('test', 'test')
        self.assertEqual(parsed_filter, dict(test='test'))

    def test_parse_range(self):
        """
        Test the parse range with upper and lower bounds returns the dictionary mongo formatted
        """
        test_lower = 0
        test_upper = 2
        parsed_filter = MongoFilterParser.parse_range('test_int', upper=test_upper, lower=test_lower)
        self.assertEqual(parsed_filter, dict(test_int={'$gt': test_lower, '$lt': test_upper}))
