from app.schema.boleto import BoletoCreate, BoletoResponse
from datetime import datetime

def gerar_boleto(dados: BoletoCreate) -> BoletoResponse:
    codigo = f"23791{datetime.now().strftime('%f')[:6]}"
    linha_digitavel = f"{codigo[:5]}.{codigo[5:10]} {codigo[10:]}"
    
    return BoletoResponse(
        nome=dados.nome,
        cpf=dados.cpf,
        valor=dados.valor,
        vencimento=dados.vencimento,
        codigo=codigo,
        linha_digitavel=linha_digitavel
    )
