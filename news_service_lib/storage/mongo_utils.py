from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


def mongo_health_check(mongo_client: MongoClient) -> bool:
    """
    Check if the mongodb storage is available

    Args:
        mongo_client: mongo database client

    Returns: True if mongodb is available, False otherwise

    """
    try:
        mongo_client.server_info()
        return True
    except ServerSelectionTimeoutError:
        return False
