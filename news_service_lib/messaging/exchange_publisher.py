"""
Exchange publisher module
"""
import json
from logging import Logger

from pika.exceptions import StreamLostError

from .exchange_provider import ExchangeProvider


class ExchangePublisher(ExchangeProvider):
    """
    Exchange publisher implementation
    """
    def __init__(self, host: str, port: str, user: str, password: str, exchange: str, logger: Logger):
        """
        Initialize the exchange publisher with the specified exchange provider configuration parameters

        Args:
            host: exchange provider host address
            port: exchange provider service port
            user: exchange provider access user
            password: exchange provider access password
            exchange: name of the exchange to publish in
        """
        super().__init__(host, port, user, password, exchange, logger)
        self._logger.info('Initializing exchange publisher for %s', exchange)

    def __call__(self, message_json: dict, reconnection: bool = False):
        """
        Publish the input message in the previously declared exchange

        Args:
            message_json: dictionary json like message to publish
            reconnection: True if the publish is been made after a reconnection, False otherwise

        """
        self._logger.info('Publishing a new message')
        try:
            self._channel.basic_publish(exchange=self._exchange, routing_key='', body=json.dumps(message_json))
        except StreamLostError as stle:
            self._logger.warning(f'Connection lost with queue provider. Retrying...')
            if not reconnection:
                self.connect()
                self.initialize()
                self(message_json, reconnection=True)
            else:
                self._logger.error(f'Fatal connection error after retrying: {stle}')
                raise ConnectionError('Error connecting to queue provider after retrying')
