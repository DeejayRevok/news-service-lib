"""
SQL database client module
"""
from logging import Logger
from sqlite3 import IntegrityError
from typing import List, Iterator, Any

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql.elements import BinaryExpression

from ..sql import SqlSessionProvider
from ..exceptions import StorageIntegrityError, StorageError
from ..sort_direction import SortDirection
from ..filter import Filter, MatchFilter
from ..filter.parsers import SQLFilterParser
from . import Storage


class SqlStorage(Storage):
    """
    SQL storage client implementation
    """

    def __init__(self, session_provider: SqlSessionProvider, model: DeclarativeMeta, logger: Logger):
        """
        Database client initializer

        Args:
            session_provider: SQLAlchemy sessions manager
            logger: logger instance to use
        """
        self._logger = logger
        self._model = model
        self._session_provider = session_provider

    def save(self, model_instance: DeclarativeMeta) -> Any:
        """
        Save the specified model to the database

        Args:
            model_instance: instance to save

        Returns: persisted instance

        """
        try:
            with self._session_provider(read_only=False) as session:
                session.add(model_instance)
                return model_instance
        except IntegrityError as interr:
            self._logger.error(f'Integrity error trying to save {model_instance}')
            raise StorageIntegrityError(str(interr)) from interr
        except Exception as ex:
            self._logger.error(f'Error trying to save {model_instance}')
            raise StorageError(str(ex))

    @staticmethod
    def _parse_keys(model: type(DeclarativeMeta), filters: List[Filter]) -> List[BinaryExpression]:
        """
        Parse the input filter keys to its SQL alchemy representation

        Args:
            model: model to parse the filters for
            filters: filters to parse

        """
        for filter_instance in filters:
            filter_key = filter_instance.key
            if hasattr(model, filter_key):
                filter_instance.key = getattr(model, filter_key)
            else:
                raise AttributeError(
                    f'{model.__name__} has not the {filter_key} property')

    def _get_all(self, session: Session,
                 filters: List[Filter] = None,
                 sort_key: str = None,
                 sort_direction: SortDirection = None) -> Query:
        """
        Get all the entities which matches the input parameters

        Args:
            session: session used to query the entities
            filters: filters to apply
            sort_key: key used to sort the results
            sort_direction: sorting direction

        Returns: filtered entities

        """
        if not filters:
            filters = list()

        query = session.query(self._model)

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
        """
        Get the entities which matches the given filters

        Args:
            filters: filters to be applied
            sort_key: key to sort the results
            sort_direction: sorting direction

        Returns: entities which matches the given filters

        """
        with self._session_provider() as session:
            return self._get_all(session, filters=filters)

    def get_one(self, filters: List[Filter] = None) -> Any:
        """
        Get one entity which matches the given filter

        Args:
            filters: filtes to apply

        Returns: entity which matches the given filters

        """
        with self._session_provider() as session:
            return self._get_all(session, filters=filters).first()

    def delete(self, identifier: Any):
        """
        Delete the entity identified by the given identifier

        Args:
            identifier: identifier of the entity to delete

        """
        try:
            with self._session_provider(read_only=False) as session:
                primary_key = self._model.primary_key.columns.values()[0].name
                self._get_all(session, filters=[MatchFilter(primary_key, identifier)]).delete()
        except Exception as ex:
            self._logger.error(f'Error trying to delete the {self._model.__class__.__name__} with id {identifier}')
            raise StorageError(str(ex))
