import ast
import asyncio
import datetime
from functools import partial
from logging import Logger
from typing import Callable, Any

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp_graphql import GraphQLView
from graphene import Schema, Scalar, Node
from graphql import ResolveInfo
from graphql.error import GraphQLLocatedError
from graphql.execution.executors.asyncio import AsyncioExecutor

GRAPHIQL_JWT_TEMPLATE = """<!--
The request to this GraphQL server provided the header "Accept: text/html"
and as a result has been presented GraphiQL - an in-browser IDE for
exploring GraphQL.
If you wish to receive JSON, provide the header "Accept: application/json" or
add "&raw" to the end of the URL within a browser.
-->
<!DOCTYPE html>
<html>
<head>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      width: 100%;
    }
    #graphiql {
      height: 100vh;
    }
    .jwt-token {
      background: linear-gradient(#f7f7f7, #e2e2e2);
      border-bottom: 1px solid #d0d0d0;
      font-family: system, -apple-system, 'San Francisco', '.SFNSDisplay-Regular', 'Segoe UI', Segoe, 'Segoe WP', 'Helvetica Neue', helvetica, 'Lucida Grande', arial, sans-serif;
      padding: 7px 14px 6px;
      font-size: 14px;
    }
  </style>
  <meta name="referrer" content="no-referrer">
  <title>GraphiQL UI</title>
  <link rel="icon" href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.8/build/favicon.png" />
  <link href="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.css" rel="stylesheet" />
  <script src="//cdn.jsdelivr.net/gh/github/fetch@3.0.0/fetch.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react@16.12.0/umd/react.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react-dom@16.12.0/umd/react-dom.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/subscriptions-transport-ws@0.9.16/browser/client.js"></script>
  <script src="//cdn.jsdelivr.net//npm/graphiql-subscriptions-fetcher@0.0.2/browser/client.js"></script>
</head>
<body>
  <div class="jwt-token">JWT Token <input id="jwt-token" placeholder="JWT Token goes here"></div>
  <div id="graphiql">Loading...</div>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });

    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }

    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };

    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }

    var subscriptionsFetcher;
    if ('{{subscriptions}}') {
      const subscriptionsClient = new SubscriptionsTransportWs.SubscriptionClient(
        '{{ subscriptions }}',
        {reconnect: true}
      );

      subscriptionsFetcher = GraphiQLSubscriptionsFetcher.graphQLFetcher(
        subscriptionsClient,
        graphQLFetcher
      );
    }

    var fetchURL = locationQuery(otherParams);
    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams) {
      const jwtToken = document.getElementById('jwt-token').value;
      let headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };
      if (jwtToken) {
        headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-API-Key': jwtToken ? `Bearer ${jwtToken}` : null
        };
      }
      return fetch(fetchURL, {
        method: 'post',
        headers: headers,
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.text();
      }).then(function (responseBody) {
        try {
          return JSON.parse(responseBody);
        } catch (error) {
          return responseBody;
        }
      });
    }

    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }

    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }

    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }

    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }

    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: subscriptionsFetcher || graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditOperationName: onEditOperationName,
        query: {{query|tojson}},
        response: {{result|tojson}},
        variables: {{variables|tojson}},
        operationName: {{operation_name|tojson}},
      }),
      document.getElementById('graphiql')
    );
  </script>
</body>
</html>"""


class CustomDateTime(Scalar):
    """
    Custom date time scalar implementation
    """
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def serialize(dt: Any) -> str:
        """
        Serialize the input date time like object

        Args:
            dt: input date time representation

        Returns: date time string representation

        """
        if not isinstance(dt, str):
            return dt.isoformat()
        else:
            return dt

    @staticmethod
    def parse_literal(node: Node) -> datetime:
        """
        Parse a string date time node to a datetime object

        Args:
            node: node to parse date time

        Returns: parsed date time

        """
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(node.value, CustomDateTime.DATE_FORMAT)

    @staticmethod
    def parse_value(value: str) -> datetime:
        """
        Parse a string date time representation

        Args:
            value: value to parse

        Returns: parsed date time string

        """
        return datetime.datetime.strptime(value, CustomDateTime.DATE_FORMAT)


def error_formatter(error: Exception, logger: Logger) -> dict:
    """
    Error formatter for GraphQL queries

    Args:
        error: query error
        logger: logger instance used to report errors

    Returns: dictionary formatted error

    """
    if isinstance(error, GraphQLLocatedError):
        error = error.original_error
    logger.error('Error in GraphQL query', exc_info=(type(error), error, error.__traceback__))
    return dict(error=error.__class__.__name__, detail=str(error))


def graph_attach_mod(app, *, route_path='/graphql', route_name='graphql', **kwargs):
    """
    Attach the Graphql view to the input aiohttp app avoiding cors problems

    Args:
        app: app to attach the GraphQL view
        route_path: URI path to the GraphQL view
        route_name: name of the route for the GraphQL view
        **kwargs: GraphQL view initialization arguments

    """
    view = GraphQLView(**kwargs)
    for method in 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD':
        app.router.add_route(method, route_path, view, name=route_name)

    if 'graphiql' in kwargs and kwargs['graphiql']:
        for method in 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD':
            app.router.add_route(method, '/graphiql', view, name='graphiql')


def setup_graphql_routes(app: Application, schema: Schema, logger: Logger):
    """
    Add the graphql routes to the specified application

    Args:
        app: application to add routes
        schema: graphene schema which describes the graphql queries and mutations
        logger: logger instance used by the different graphene utilities functions

    """
    graph_attach_mod(app,
                     route_path='/graphql',
                     schema=schema,
                     graphiql=True,
                     graphiql_template=GRAPHIQL_JWT_TEMPLATE,
                     executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
                     enable_async=True,
                     error_formatter=partial(error_formatter, logger=logger))


def login_required(func: Callable):
    """
    Decorator used to check if the request is authenticated

    Args:
        func: function to decorate

    Returns: decorated function checking the authentication

    """
    def wrapper(*args, **kwargs):
        graphql_info = None
        for arg in args:
            if isinstance(arg, ResolveInfo):
                graphql_info = arg
                break
        if not graphql_info:
            raise ValueError('GraphQL resolve info not found')
        request = graphql_info.context['request']
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(*args, **kwargs)
    return wrapper
