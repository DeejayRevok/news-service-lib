"""
Engine types module
"""
from enum import Enum


class SqlEngineType(Enum):
    """
    Type of SQL engine
    """
    MYSQL = 'mysql://{user}:{password}@{host}:{port}/{database}'
    SQLITE = 'sqlite:///:memory:'

    @property
    def uri(self) -> str:
        return self.value
