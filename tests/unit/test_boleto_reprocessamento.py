from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from app.core.mongo import boletos_collection
from app.core.redis_client import redis_client
from app.main import app
from app.services.boleto_service import concluir_reprocessamento


@pytest.fixture
def boleto_com_erro():
    # Inclui o formato de código usado pelas versões anteriores.
    codigo = str(uuid4().int)[:11]
    resultado = boletos_collection.insert_one({
        "nome": "João da Silva",
        "cpf": "12345678900",
        "valor": 150.0,
        "vencimento": "2025-12-31",
        "codigo": codigo,
        "linha_digitavel": "99999.99999 99999",
        "status": "erro",
    })
    try:
        yield codigo
    finally:
        boletos_collection.delete_one({"_id": resultado.inserted_id})


def test_reprocessamento_concorrente_aceita_uma_solicitacao(boleto_com_erro):
    codigo = boleto_com_erro
    path = f"/boletos/{codigo}/reprocessar"
    with TestClient(app) as client, ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(client.post, [path, path]))
        assert sorted(resposta.status_code for resposta in respostas) == [200, 400]
        sucesso = next(resposta for resposta in respostas if resposta.status_code == 200)
        assert sucesso.json()["mensagem"] == "Boleto enviado para reprocessamento"
        assert client.get(f"/boletos/{codigo}").json()["status"] == "reprocessando"


def test_worker_recupera_reprocessamento_sem_notificacao(boleto_com_erro, monkeypatch):
    codigo = boleto_com_erro

    def indisponivel(*_args):
        raise ConnectionError("Redis indisponível")

    monkeypatch.setattr(redis_client, "rpush", indisponivel)
    with TestClient(app) as client:
        assert client.post(f"/boletos/{codigo}/reprocessar").status_code == 200
        assert concluir_reprocessamento(codigo)
        assert not concluir_reprocessamento(codigo)
        assert client.get(f"/boletos/{codigo}").json()["status"] == "enviado"
