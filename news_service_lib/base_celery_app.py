"""
Base celery application module
"""
import sys
from typing import List

from celery import Celery


class BaseCeleryApp:
    """
    Celery worker application implementation
    """
    BASE_BROKER_URL = 'pyamqp://{user}:{password}@{host}:{port}//'

    def __init__(self, app_name: str, task_imports: List[str] = None):
        """
        Initialize the celery application

        Args:
            app_name: Celery application name
            task_imports: List of module routes where the Celery tasks are located
        """
        self.app = Celery(app_name, include=task_imports)

    def configure(self, task_queue_name: str = None, broker_config: dict = None, worker_concurrency: int = None):
        """
        Configure the current celery application in order to set the broker service configuration
        and the worker concurrency number

        Args:
            task_queue_name: name of the default task queue
            broker_config: broker service configuration
            worker_concurrency: number of worker concurrent threads

        """
        config_dict = dict()
        if task_queue_name:
            config_dict['task_default_queue'] = task_queue_name
        if broker_config:
            broker_url = self.BASE_BROKER_URL.format(**broker_config)
            config_dict['broker_url'] = broker_url
            config_dict['result_backend'] = 'rpc://'
        if worker_concurrency:
            config_dict['worker_concurrency'] = worker_concurrency

        if len(config_dict.keys()):
            self.app.config_from_object(config_dict)

    def run(self, beat: bool = False):
        """
        Run the associated celery app

        Returns:

        """
        sys.argv = [sys.argv[0]]
        self.app.worker_main() if not beat else self.app.Beat().run()
