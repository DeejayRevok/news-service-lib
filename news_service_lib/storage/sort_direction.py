"""
Storage sorting types definitions module
"""
from enum import Enum

import pymongo
from sqlalchemy import asc, desc


class SortDirection(Enum):
    """
    Storage results sorting type definition:
    - ASC = ascending sorting
    - DESC = descending sorting
    """
    ASC = [pymongo.ASCENDING, asc]
    DESC = [pymongo.DESCENDING, desc]
