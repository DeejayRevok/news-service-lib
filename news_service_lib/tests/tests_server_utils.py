"""
Server utils test module
"""
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

from aiohttp import web
from aiohttp.web_app import Application

from ..config import ConfigProfile, Configuration
from ..server_utils import initialize_server, finish_server_startup, server_runner


class TestServerUtils(TestCase):
    """
    Server utils test cases implementation
    """

    @patch('news_service_lib.server_utils.add_logstash_handler')
    @patch('news_service_lib.config.configparser')
    def test_initialize_sever(self, mock_configparser, add_logstash_mock):
        """
        Test the server initialization adds config, host and port
        """
        mock_configparser.RawConfigParser.return_value = MagicMock()
        app = initialize_server(ConfigProfile.LOCAL, 'test', dict(test='test'))
        add_logstash_mock.assert_called_once()
        self.assertIsNotNone(app['config'])
        self.assertIsNotNone(app['host'])
        self.assertIsNotNone(app['port'])

    @patch.object(Configuration, 'get')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec')
    @patch('news_service_lib.server_utils.ElasticAPM')
    @patch('news_service_lib.server_utils.Client')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec_mod')
    def test_finish_server_startup_basepath(self, apispec_mod_mock, apm_client_mock, apm_mock, apispec_mock,
                                            config_mock):
        """
        Test the finish server with basepath specified setups the apm server connection and the modified api spec
        """
        os.environ.update({'SERVER_BASEPATH': 'test'})
        app = Application()
        app['config'] = config_mock
        app = finish_server_startup(app, 'test')
        apispec_mod_mock.assert_called_once()
        self.assertFalse(apispec_mock.called)
        apm_client_mock.assert_called_once()
        apm_mock.assert_called_once()
        self.assertIsNotNone(app['apm'])

    @patch.object(Configuration, 'get')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec')
    @patch('news_service_lib.server_utils.ElasticAPM')
    @patch('news_service_lib.server_utils.Client')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec_mod')
    def test_finish_server_startup_not_basepath(self, apispec_mod_mock, apm_client_mock, apm_mock, apispec_mock,
                                                config_mock):
        """
        Test the finish server without basepath specified setups the apm server connection and the straight api spec
        """
        os.environ.clear()
        app = Application()
        app['config'] = config_mock
        app = finish_server_startup(app, 'test')
        apispec_mock.assert_called_once()
        self.assertFalse(apispec_mod_mock.called)
        apm_client_mock.assert_called_once()
        apm_mock.assert_called_once()
        self.assertIsNotNone(app['apm'])

    @patch('news_service_lib.server_utils.aiohttp_cors')
    @patch.object(Configuration, 'get')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec')
    @patch('news_service_lib.server_utils.ElasticAPM')
    @patch('news_service_lib.server_utils.Client')
    @patch('news_service_lib.server_utils.setup_aiohttp_apispec_mod')
    def test_finish_server_startup_configure_cors(self, _, __, ___, ____,
                                                  config_mock, cors_lib_mock):
        """
        Test the finish server setups the CORS settings and adds all the routes to the configured CORS
        """
        cors_mock = MagicMock()
        cors_lib_mock.setup.return_value = cors_mock
        os.environ.update({'SERVER_BASEPATH': 'test'})
        app = Application()
        app.add_routes([
            web.get('/testpath1', MagicMock(), allow_head=False),
            web.get('/testpath2', MagicMock(), allow_head=False)
        ])
        app['config'] = config_mock
        app = finish_server_startup(app, 'test')

        cors_lib_mock.setup.assert_called_once()
        routes_num = len(app.router.routes())
        if routes_num > 0:
            self.assertEqual(routes_num, len([call for call in cors_mock.method_calls if call[0] == 'add']))

    @patch('news_service_lib.server_utils.run_app')
    @patch('news_service_lib.server_utils.initialize_server')
    @patch('news_service_lib.server_utils.finish_server_startup')
    @patch('news_service_lib.server_utils.profile_args_parser')
    def test_server_runner(self, argparser_mock, finish_server_mock, init_server_mock, run_app_mock):
        """
        Test the server runner initializes the server, calls to server initializer function,
        finishes the server initialization and runs the obtained app
        """
        server_initializer_mock = MagicMock()
        argparser_mock.return_value = {'profile': 'LOCAL'}
        logger_provider_mock = MagicMock()
        manager = Mock()
        manager.attach_mock(init_server_mock, 'init_server_mock')
        manager.attach_mock(server_initializer_mock, 'server_initializer_mock')
        manager.attach_mock(finish_server_mock, 'finish_server_mock')
        manager.attach_mock(run_app_mock, 'run_app_mock')
        app = Application()
        app['host'] = 'test'
        app['port'] = 0
        finish_server_mock.return_value = app
        server_runner('test', server_initializer_mock, 'test', 'test', dict(test='test'), logger_provider_mock)
        self.assertListEqual(list(map(lambda mock_call: mock_call[0], manager.method_calls)),
                             ['init_server_mock', 'server_initializer_mock', 'finish_server_mock', 'run_app_mock'])
        argparser_mock.assert_called_once()
        logger_provider_mock.assert_called_once()
