import json
import logging
import time

from redis.exceptions import RedisError

from app.core.redis_client import redis_client

log = logging.getLogger(__name__)


def consumir_boletos():
    log.info("Worker de emissão iniciado")
    while True:
        try:
            evento = redis_client.blpop("fila_boletos", timeout=2)
            if evento:
                codigo = json.loads(evento[1])["codigo"]
                log.info("Primeira tentativa simulada com erro para %s", codigo)
        except RedisError:
            log.warning("Redis indisponível na fila de emissão")
            time.sleep(2)
        except (ValueError, KeyError, TypeError):
            log.warning("Evento de emissão inválido")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumir_boletos()
