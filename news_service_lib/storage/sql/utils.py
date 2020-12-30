"""
SQL utilities module
"""
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta

from .engine_type import SqlEngineType


def init_sql_db(base: DeclarativeMeta, engine: Engine, alembic_ini_path: str = None):
    """
    Initialize the sql database schema defined by the base input schema running the migrations if it is needed

    Args:
        base: database base schema
        engine: database engine used to create the tables
        alembic_ini_path: alembic tool initialization file

    """
    base.metadata.bind = engine
    if alembic_ini_path:
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_section_option('alembic', 'sqlalchemy.url', str(engine.url))
        if len(inspect(engine).get_table_names()):
            command.upgrade(alembic_cfg, "head")
        else:
            base.metadata.create_all()
            command.stamp(alembic_cfg, "head")
    else:
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
