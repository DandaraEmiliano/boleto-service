from app.core import redis_client
from fastapi import FastAPI
from app.api import boleto
import json


app = FastAPI(
    title="Boleto Service",
    description="API for generating boletos",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(boleto.router)

try:
    redis_client.rpush("fila_teste", json.dumps({"msg": "funcionando"}))
    print("Redis funcionando (rpush ok)")
except Exception as e:
    print("Erro no Redis:", e)