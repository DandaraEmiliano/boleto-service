from fastapi.testclient import TestClient

from app.main import create_app
from app.services import demo

DADOS = {
    "nome": "Marina Exemplo",
    "cpf": "00000000000",
    "valor": "149.90",
    "vencimento": "2027-01-12",
}


def test_fluxo_publico_isola_boletos_e_gera_pdf(monkeypatch):
    agora = 100.0
    monkeypatch.setattr(demo, "monotonic", lambda: agora)
    app = create_app(demo_mode=True)
    with TestClient(app) as titular, TestClient(app) as visitante:
        page = titular.get("/")
        assert page.status_code == 200
        assert "Painel de boletos" in page.text
        assert titular.get("/assets/app.js").status_code == 200

        criado = titular.post("/boletos", json=DADOS)
        assert criado.status_code == 200
        assert criado.json()["status"] == "erro"
        assert "HttpOnly" in criado.headers["set-cookie"]
        path = f"/boletos/{criado.json()['codigo']}"

        assert len(titular.get("/boletos/status/erro").json()) == 1
        assert visitante.get("/boletos/status/erro").json() == []
        assert visitante.get(path).status_code == 404
        assert visitante.get(f"{path}/pdf").status_code == 404
        assert visitante.post(f"{path}/reprocessar").status_code == 404

        pdf = titular.get(f"{path}/pdf")
        assert pdf.content.startswith(b"%PDF")
        assert pdf.headers["cache-control"] == "no-store"

        assert titular.post(f"{path}/reprocessar").status_code == 200
        assert titular.get(path).json()["status"] == "reprocessando"
        assert titular.post(f"{path}/reprocessar").status_code == 400
        agora += 2
        assert titular.get(path).json()["status"] == "enviado"
        assert titular.get("/boletos/status/erro").json() == []


def test_demo_rejeita_pagador_fora_da_lista():
    with TestClient(create_app(demo_mode=True)) as client:
        resposta = client.post("/boletos", json={**DADOS, "cpf": "12345678900"})
        assert resposta.status_code == 422
        assert client.cookies.get("boleto_demo") is None


def test_cookie_da_demo_publica_exige_https():
    with TestClient(create_app(demo_mode=True, secure_cookie=True), base_url="https://testserver") as client:
        assert "Secure" in client.post("/boletos", json=DADOS).headers["set-cookie"]


def test_api_rejeita_valor_com_fracao_de_centavo():
    with TestClient(create_app(demo_mode=True)) as client:
        assert client.post("/boletos", json={**DADOS, "valor": "12.001"}).status_code == 422
