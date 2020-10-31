from logging import Logger

from .implementation.sql_storage import SqlStorage
from .implementation.mongo_storage import MongoStorage
from .storage_type import StorageType
from .implementation.storage import Storage
from .storage_watcher import StorageWatcher
from .sort_direction import SortDirection
from .exceptions import StorageError, StorageIntegrityError


def storage_factory(stor_type: str, storage_config: dict, logger: Logger) -> Storage:
    """
    Get the specified storage implementation

    Args:
        stor_type: type of the storage
        storage_config: storage configuration parameters
        logger: logger instance used by the storage interface

    Returns: configured storage implementation

    """
    if stor_type in list(map(lambda stor_typ: stor_typ.value, StorageType)):
        stor = StorageType[stor_type]

        if stor == StorageType.MONGO:
            return MongoStorage(**storage_config, logger=logger)
        elif stor == StorageType.SQL:
            return SqlStorage(**storage_config, logger=logger)
    else:
        raise NotImplementedError('Specified storage type not implemented')


__all__ = [
    "StorageType",
    "StorageWatcher",
    "SortDirection",
    "StorageError",
    "StorageIntegrityError",
    "storage_factory"
]
