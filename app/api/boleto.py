from fastapi import APIRouter, HTTPException
import json
from typing import List
from fastapi import APIRouter

from app.core.redis_client import redis_client
from app.core.mongo import boletos_collection
from app.schema.boleto import BoletoCreate, BoletoResponse
from app.services.boleto_service import gerar_boleto, buscar_boleto_por_codigo
from app.utils.pdf_generator import gerar_pdf_boleto
from fastapi.responses import Response

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
    
@router.get("/boletos/status/erro", response_model=List[BoletoResponse])
def listar_boletos_com_erro():
    boletos = boletos_collection.find({"status": "erro"}, {"_id": 0})
    return list(boletos)

@router.post("/boletos/{codigo}/reprocessar")
def reprocessar_boleto(codigo: str):
    boleto = boletos_collection.find_one({"codigo": codigo})
    if not boleto:
        raise HTTPException(status_code=404, detail="Boleto não encontrado")
    if boleto["status"] != "erro":
        raise HTTPException(status_code=400, detail="Boleto não está com status de erro")

    boleto["_id"] = str(boleto["_id"]) 
    redis_client.rpush("fila_reprocessamento", json.dumps(boleto)) 
    return {"mensagem": "Boleto enviado para reprocessamento"}
