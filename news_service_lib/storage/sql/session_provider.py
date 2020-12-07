from typing import Optional, Any

from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session


class SqlSessionProvider:

    def __init__(self, engine: Engine):
        self._session_factory = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
        self._session: Optional[Session] = None
        self._nesting = 0

    def __call__(self, read_only: bool = True):
        if self._nesting <= 0:
            self._session = self._session_factory()
            self._session.info['read_only'] = read_only
        return self

    def __enter__(self):
        self._nesting += 1
        if self._session:
            return self._session
        else:
            raise ValueError('Session not provided, call the session provider in order to get it')

    def __exit__(self, _, exc_val: Exception, __):
        self._nesting -= 1
        if self._nesting <= 0:
            if exc_val:
                self._session.rollback()
            elif not self._session.info['read_only']:
                try:
                    self._session.commit()
                except Exception as inner_exc:
                    self._session.rollback()
                    raise inner_exc
            self._session.close()
        if exc_val:
            raise exc_val

    @property
    def query_property(self):
        return self._session_factory.query_property()

    @query_property.setter
    def query_property(self, value: Any):
        raise ValueError('The property query_property is not writable')
