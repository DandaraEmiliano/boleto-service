from fastapi import APIRouter
from app.schema.boleto import BoletoCreate, BoletoResponse
from app.services.boleto_service import gerar_boleto, buscar_boleto_por_codigo
from fastapi.responses import Response
from app.utils.pdf_generator import gerar_pdf_boleto


router = APIRouter()

@router.post("/boletos", response_model=BoletoResponse)
def criar_boleto(boleto: BoletoCreate):
    return gerar_boleto(boleto)


@router.get("/boletos/{codigo}", response_model=BoletoResponse)
def reemitir_boleto(codigo: str):
    try:
        return buscar_boleto_por_codigo(codigo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/boletos/{codigo}/pdf")
def gerar_pdf(codigo: str):
    try:
        boleto = buscar_boleto_por_codigo(codigo)
        pdf_bytes = gerar_pdf_boleto(boleto.dict())
        return Response(content=pdf_bytes, media_type="application/pdf")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))