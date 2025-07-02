from fastapi import APIRouter
from app.schema.boleto import BoletoCreate, BoletoResponse
from app.services.boleto_service import gerar_boleto

router = APIRouter()

@router.post("/boletos", response_model=BoletoResponse)
def criar_boleto(boleto: BoletoCreate):
    return gerar_boleto(boleto)
