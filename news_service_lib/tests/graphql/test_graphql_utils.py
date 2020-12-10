"""
GraphQL utils tests module
"""
import datetime
from logging import getLogger
from unittest import TestCase
from unittest.mock import patch, MagicMock

from aiohttp.web_app import Application
from graphene import Field
from graphql.error import GraphQLLocatedError

from ...graphql.graphql_utils import error_formatter, graph_attach_mod, setup_graphql_routes
from ...graphql import CustomDateTime

LOGGER = getLogger()


class TestGraphQLUtils(TestCase):
    """
    GraphQL utils test cases
    """
    def test_serialize_custom_datetime(self):
        """
        Test if serializing the datetime returns string
        """
        self.assertIsInstance(CustomDateTime.serialize(datetime.datetime.now()), str)
        self.assertIsInstance(CustomDateTime.serialize('test'), str)
        self.assertIsInstance(CustomDateTime.serialize(datetime.datetime.now().timestamp()), str)

    def test_parse_value_datetime(self):
        """
        Test parsing the string datetime value returns datetime instance
        """
        self.assertIsInstance(CustomDateTime.parse_value('2020-12-10T13:37:49'), datetime.datetime)

    def test_error_formatter(self):
        """
        Test error formatter for graphql error returns origin error formatted in a dictionary
        """
        gql_error = GraphQLLocatedError([Field('test')], original_error=Exception('Test exception'))
        formatted_error = error_formatter(gql_error, LOGGER)
        self.assertEqual(dict(error='Exception', detail='Test exception'), formatted_error)

    @patch('news_service_lib.graphql.graphql_utils.GraphQLView')
    def test_attach_mod(self, _):
        """
        Test attach mod adds the graphiql and graphql routes to the web app
        """
        app = Application()
        graph_attach_mod(app, graphiql=True)
        app_resources = [resource._path for resource in app.router.resources()]
        self.assertIn('/graphiql', app_resources)
        self.assertIn('/graphql', app_resources)

    @patch('news_service_lib.graphql.graphql_utils.graph_attach_mod')
    def test_setup_graph_routes(self, attach_mock):
        """
        Test setting up the graphql routes calls attach mod with the web application and the graphql schema
        """
        app_mock = MagicMock()
        schema_mock = MagicMock()
        setup_graphql_routes(app_mock, schema_mock, None)
        self.assertEqual(attach_mock.call_args[0][0], app_mock)
        self.assertEqual(attach_mock.call_args[1]['schema'], schema_mock)



