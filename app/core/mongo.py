from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["boleto_db"]
boletos_collection = db["boletos"]
