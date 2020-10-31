"""
SQL database client module
"""
from logging import Logger
from sqlite3 import IntegrityError
from typing import List, Iterator, Any

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql.elements import BinaryExpression

from ..exceptions import StorageIntegrityError, StorageError
from ..sort_direction import SortDirection
from ..filter import Filter, MatchFilter
from ..filter.parsers import SQLFilterParser
from . import Storage


class SqlStorage(Storage):
    """
    SQL storage client implementation
    """

    MYSQL_URL = 'mysql://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, engine: Engine, model: DeclarativeMeta, logger: Logger):
        """
        Database client initializer

        Args:
            engine
            logger: logger instance to use
        """
        self._logger = logger
        self._model = model
        self._engine = engine
        session_maker = sessionmaker(bind=self._engine)
        self._session = session_maker()

    def save(self, model_instance: DeclarativeMeta) -> Any:
        """
        Save the specified model to the database

        Args:
            model_instance: instance to save

        Returns: persisted instance

        """
        try:
            self._session.add(model_instance)
            self._session.commit()
            self._session.flush()
            return model_instance
        except IntegrityError as interr:
            self.rollback()
            self._logger.error(f'Integrity error trying to save {model_instance}')
            raise StorageIntegrityError(str(interr)) from interr
        except Exception as ex:
            self.rollback()
            self._logger.error(f'Error trying to save {model_instance}')
            raise StorageError(str(ex))

    @staticmethod
    def _parse_keys(model: type(DeclarativeMeta), filters: List[Filter]) -> List[BinaryExpression]:
        for filter_instance in filters:
            filter_key = filter_instance.key
            if hasattr(model, filter_key):
                filter_instance.key = getattr(model, filter_key)
            else:
                raise AttributeError(
                    f'{model.__name__} has not the {filter_key} property')

    def _get_all(self, filters: List[Filter] = None,
                 sort_key: str = None,
                 sort_direction: SortDirection = None) -> Query:
        if not filters:
            filters = list()

        query = self._session.query(self._model)

        if filters:
            self._parse_keys(self._model, filters)

        filters_list = list()
        for filter_instance in filters:
            filters_list.append(*filter_instance.parse_filter(SQLFilterParser))

        filtered_query = query.filter(*filters_list)

        if sort_key:
            return filtered_query.order_by(sort_direction.value[1](getattr(self._model, sort_key)))
        else:
            return filtered_query

    def get(self, filters: List[Filter] = None,
            sort_key: str = None,
            sort_direction: SortDirection = None) -> Iterator[DeclarativeMeta]:
        return self._get_all(filters=filters)

    def get_one(self, filters: List[Filter] = None) -> Any:
        return self._get_all(filters=filters).first()

    def delete(self, identifier: Any):
        primary_key = self._model.primary_key.columns.values()[0].name
        try:
            self._get_all(filters=[MatchFilter(primary_key, identifier)]).delete()
        except Exception as ex:
            self.rollback()
            self._logger.error(f'Error trying to delete the {self._model.__class__.__name__} with id {identifier}')
            raise StorageError(str(ex))

    def rollback(self):
        """
        Perform a rollback operation for the current storage session
        """
        self._session.rollback()
