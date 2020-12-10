""" Storage errors definition"""


class StorageError(Exception):
    """ Database errors base class"""


class StorageIntegrityError(StorageError):
    """ Database integrity error class"""
