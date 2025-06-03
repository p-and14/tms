from pymongo import MongoClient

from src.core.config import settings


mongo_client = MongoClient(settings.MONGO_URL_noauth)
mongo_db = mongo_client[f"{settings.MONGO_DB}"]
