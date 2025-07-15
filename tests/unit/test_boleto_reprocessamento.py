from fastapi.testclient import TestClient
from app.main import app
from app.core.mongo import boletos_collection

client = TestClient(app)

def test_reprocessar_boleto_com_status_erro():
    boleto = {
        "nome": "João da Silva",
        "cpf": "12345678900",
        "valor": 150.0,
        "vencimento": "2025-12-31",
        "codigo": "999999",
        "linha_digitavel": "99999.99999 99999",
        "status": "erro"
    }
    boletos_collection.insert_one(boleto)

    response = client.post("/boletos/999999/reprocessar")
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Boleto enviado para reprocessamento"
