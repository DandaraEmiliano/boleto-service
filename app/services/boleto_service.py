from app.core.redis_client import redis_client
from app.schema.boleto import BoletoCreate, BoletoResponse
from app.core.mongo import boletos_collection
from datetime import datetime, date
import json

def gerar_boleto(dados: BoletoCreate) -> BoletoResponse:
    codigo = f"23791{datetime.now().strftime('%f')[:6]}"
    linha_digitavel = f"{codigo[:5]}.{codigo[5:10]} {codigo[10:]}"
    
    boleto = {
        "nome": dados.nome,
        "cpf": dados.cpf,
        "valor": dados.valor,
        "vencimento": dados.vencimento.isoformat(),
        "codigo": codigo,
        "linha_digitavel": linha_digitavel
    }

    result = boletos_collection.insert_one(boleto)
    boleto["_id"] = str(result.inserted_id)

    redis_client.rpush("fila_boletos", json.dumps(boleto))
    
    return BoletoResponse(**boleto)

def buscar_boleto_por_codigo(codigo: str) -> BoletoResponse:
    boleto = boletos_collection.find_one({"codigo": codigo}, {"_id": 0})
    if not boleto:
        raise ValueError("Boleto não encontrado")

    boleto["vencimento"] = date.fromisoformat(boleto["vencimento"])
    return BoletoResponse(**boleto)
