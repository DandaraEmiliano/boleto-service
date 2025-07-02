import json
import time
from app.core.redis_client import redis_client

def consumir_boletos():
    print("Worker iniciado. Aguardando boletos...")
    while True:
        _, dado = redis_client.blpop("fila_boletos")
        boleto = json.loads(dado)
        print(f"Simulando envio do boleto {boleto['codigo']} para o banco...")
        time.sleep(2)
        print(f"Boleto {boleto['codigo']} enviado com sucesso!")

if __name__ == "__main__":
    consumir_boletos()
