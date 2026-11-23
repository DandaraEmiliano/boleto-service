from os import getenv

from pymongo import MongoClient

client = MongoClient(getenv("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
db = client[getenv("MONGO_DATABASE", "boleto_db")]
boletos_collection = db["boletos"]
