"""
Storage types module
"""
from enum import Enum


class StorageType(Enum):
    """
    Storage type enum:
        MONGO: MongoDB storage type
        SQL: SQL storage type
    """
    MONGO = 'MONGO'
    SQL = 'SQL'
