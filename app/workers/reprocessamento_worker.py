import json
import logging
import time

from pymongo import ASCENDING
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from app.core.mongo import boletos_collection
from app.core.redis_client import redis_client
from app.services.boleto_service import concluir_reprocessamento

log = logging.getLogger(__name__)


def reprocessar_boletos():
    boletos_collection.create_index([("status", ASCENDING), ("codigo", ASCENDING)])
    boletos_collection.create_index("codigo")
    log.info("Worker de reprocessamento iniciado")
    while True:
        try:
            # O MongoDB registra o trabalho pendente antes da publicação no Redis.
            concluiu = concluir_reprocessamento()
            evento = redis_client.blpop("fila_reprocessamento", timeout=2) if not concluiu else (
                None, redis_client.lpop("fila_reprocessamento")
            )
            if evento and evento[1]:
                concluir_reprocessamento(json.loads(evento[1])["codigo"])
        except (PyMongoError, RedisError):
            log.warning("Dependência indisponível durante o reprocessamento")
            time.sleep(2)
        except (ValueError, KeyError, TypeError):
            log.warning("Evento de reprocessamento inválido")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reprocessar_boletos()
