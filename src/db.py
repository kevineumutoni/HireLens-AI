from pymongo import MongoClient
from src.config.settings import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]

jobs_col       = db["jobs"]
candidates_col = db["candidates"]
results_col    = db["screening_results"]