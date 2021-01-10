"""
Base celery app tests module
"""
import sys
from unittest import TestCase
from unittest.mock import patch

from ..base_celery_app import BaseCeleryApp


class TestBaseCeleryApp(TestCase):
    """
    Base Celery App test cases implementation
    """
    TEST_BROKER_CONFIG = {
        'host': 'test_host',
        'port': '0',
        'user': 'test_user',
        'password': 'test_password'
    }
    TEST_CONCURRENCY = 1
    TEST_QUEUE_NAME = 'test_queue'

    @patch('news_service_lib.base_celery_app.Celery')
    def setUp(self, _):
        """
        Setup the test variables
        """
        self.celery_app = BaseCeleryApp('test_app')

    def test_configure(self):
        """
        Test the configure method sets the broker url with the correct format,
        the result backend and the worker concurrency
        """
        self.celery_app.configure(task_queue_name=self.TEST_QUEUE_NAME,
                                  broker_config=self.TEST_BROKER_CONFIG,
                                  worker_concurrency=self.TEST_CONCURRENCY)
        self.celery_app.app.config_from_object.assert_called_with(
            dict(task_default_queue=self.TEST_QUEUE_NAME,
                 broker_url=f'pyamqp://{self.TEST_BROKER_CONFIG["user"]}:{self.TEST_BROKER_CONFIG["password"]}'
                            f'@{self.TEST_BROKER_CONFIG["host"]}:{self.TEST_BROKER_CONFIG["port"]}//',
                 result_backend='rpc://',
                 worker_concurrency=self.TEST_CONCURRENCY))

    def test_run(self):
        """
        Test the run method resets the system argument and starts the celery worker
        """
        self.celery_app.run()
        self.assertEqual(len(sys.argv), 1)
        self.celery_app.app.worker_main.assert_called_once()