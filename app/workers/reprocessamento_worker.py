import json
import time
from app.core.redis_client import redis_client
from app.core.mongo import boletos_collection

def reprocessar_boletos():
    print("Worker de reprocessamento iniciado...")
    while True:
        _, dado = redis_client.blpop("fila_reprocessamento")
        boleto = json.loads(dado)

        print(f"Reprocessando boleto {boleto['codigo']}...")
        time.sleep(2)

        boletos_collection.update_one(
            {"codigo": boleto["codigo"]},
            {"$set": {"status": "enviado"}}
        )
        print(f"Boleto {boleto['codigo']} reprocessado com sucesso!")

if __name__ == "__main__":
    reprocessar_boletos()
