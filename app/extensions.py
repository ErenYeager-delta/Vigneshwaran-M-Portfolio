import os
import certifi
from pymongo import MongoClient
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cache = Cache()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

# ─── MongoDB Setup ───────────────────────────────────────────────────────────
_mongo_client = None

def get_mongo_client():
    """Central MongoDB client provider."""
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            return None
        _mongo_client = MongoClient(uri, tlsCAFile=certifi.where())
    return _mongo_client

def get_mongo_db(db_name="portfolioDB"):
    """Central MongoDB database connection helper."""
    client = get_mongo_client()
    if client is None:
        return None
    return client[db_name]
