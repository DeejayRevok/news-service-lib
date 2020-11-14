from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta

from .engine_type import SqlEngineType


def init_sql_db(base: DeclarativeMeta, engine: Engine):
    """
    Initialize the sql database schema defined by the base input schema

    Args:
        base: database base schema
        engine: database engine used to create the tables

    """
    base.metadata.bind = engine
    base.metadata.create_all()


def create_sql_engine(engine_type: SqlEngineType, **engine_config) -> Engine:
    """
    Create the sql base engine

    Args:
        engine_type: type of the engine to create
        **engine_config: engine configuration params

    Returns: created engine wof the provided type with the specified configuration

    """
    return create_engine(engine_type.uri.format(**engine_config))


def sql_health_check(engine: Engine) -> bool:
    """
    Check if the storage is available

    Returns: True if the storage is available, False otherwise

    """
    try:
        engine.execute('SELECT 1 AS is_alive')
        return True
    except Exception:
        return False
