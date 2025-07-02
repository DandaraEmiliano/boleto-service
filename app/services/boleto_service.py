from app.schema.boleto import BoletoCreate, BoletoResponse
from datetime import datetime

boletos_db = {}

def gerar_boleto(dados: BoletoCreate) -> BoletoResponse:
    codigo = f"23791{datetime.now().strftime('%f')[:6]}"
    linha_digitavel = f"{codigo[:5]}.{codigo[5:10]} {codigo[10:]}"
    
    boleto = BoletoResponse(
        nome=dados.nome,
        cpf=dados.cpf,
        valor=dados.valor,
        vencimento=dados.vencimento,
        codigo=codigo,
        linha_digitavel=linha_digitavel
    )

    boletos_db[codigo] = boleto
    return boleto

def buscar_boleto_por_codigo(codigo: str) -> BoletoResponse:
    boleto = boletos_db.get(codigo)
    if not boleto:
        raise ValueError("Boleto não encontrado")
    return boleto