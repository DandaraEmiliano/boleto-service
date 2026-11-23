import json
import logging
from uuid import uuid4

from pymongo import ReturnDocument
from redis.exceptions import RedisError

from app.core.mongo import boletos_collection
from app.core.redis_client import redis_client
from app.schema.boleto import BoletoCreate, BoletoResponse

log = logging.getLogger(__name__)


class BoletoNaoEncontrado(Exception):
    pass


class BoletoForaDeEstado(Exception):
    pass


def novo_boleto(dados: BoletoCreate) -> BoletoResponse:
    codigo = f"BLT-{uuid4().hex}"
    identificador = codigo[4:16].upper()
    linha = " ".join(identificador[i:i + 4] for i in range(0, len(identificador), 4))
    return BoletoResponse(
        **dados.model_dump(exclude={"valor"}),
        valor=float(dados.valor),
        codigo=codigo,
        linha_digitavel=f"SIMULAÇÃO {linha}",
        status="erro",
    )


def notificar_fila(fila: str, codigo: str) -> None:
    try:
        redis_client.rpush(fila, json.dumps({"codigo": codigo}))
    except RedisError:
        log.warning("Redis indisponível para %s", fila)


def gerar_boleto(dados: BoletoCreate) -> BoletoResponse:
    boleto = novo_boleto(dados)
    boletos_collection.insert_one({"_id": boleto.codigo, **boleto.model_dump(mode="json")})
    notificar_fila("fila_boletos", boleto.codigo)
    return boleto


def buscar_boleto_por_codigo(codigo: str) -> BoletoResponse:
    boleto = boletos_collection.find_one({"codigo": codigo}, {"_id": 0})
    if boleto is None:
        raise BoletoNaoEncontrado
    return BoletoResponse.model_validate(boleto)


def listar_erros() -> list[BoletoResponse]:
    boletos = boletos_collection.find({"status": "erro"}, {"_id": 0})
    return [BoletoResponse.model_validate(boleto) for boleto in boletos]


def solicitar_reprocessamento(codigo: str) -> None:
    boleto = boletos_collection.find_one_and_update(
        {"codigo": codigo, "status": "erro"},
        {"$set": {"status": "reprocessando"}},
        projection={"_id": 1},
    )
    if boleto is None:
        if boletos_collection.find_one({"codigo": codigo}, {"_id": 1}) is None:
            raise BoletoNaoEncontrado
        raise BoletoForaDeEstado
    notificar_fila("fila_reprocessamento", codigo)


def concluir_reprocessamento(codigo: str | None = None) -> bool:
    filtro = {"status": "reprocessando"}
    if codigo is not None:
        filtro["codigo"] = codigo
    boleto = boletos_collection.find_one_and_update(
        filtro,
        {"$set": {"status": "enviado"}},
        projection={"_id": 1},
        return_document=ReturnDocument.AFTER,
    )
    return boleto is not None
