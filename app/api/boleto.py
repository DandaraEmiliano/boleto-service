from secrets import token_urlsafe
import re

from fastapi import APIRouter, HTTPException, Request, Response

from app.schema.boleto import BoletoCreate, BoletoResponse
from app.services import boleto_service
from app.services.demo import PAGADORES_DEMO
from app.utils.pdf_generator import gerar_pdf_boleto

router = APIRouter()
COOKIE = "boleto_demo"


def sessao(request: Request) -> str | None:
    valor = request.cookies.get(COOKIE, "")
    return valor if re.fullmatch(r"[A-Za-z0-9_-]{43}", valor) else None


def buscar(request: Request, codigo: str) -> BoletoResponse:
    if request.app.state.demo is not None:
        return request.app.state.demo.buscar(sessao(request), codigo)
    return boleto_service.buscar_boleto_por_codigo(codigo)


@router.post("/boletos", response_model=BoletoResponse)
def criar_boleto(boleto: BoletoCreate, request: Request, response: Response):
    demo = request.app.state.demo
    if demo is None:
        return boleto_service.gerar_boleto(boleto)
    if PAGADORES_DEMO.get(boleto.nome) != boleto.cpf:
        raise HTTPException(status_code=422, detail="Selecione um dos pagadores fictícios da demo.")
    titular = sessao(request) or token_urlsafe(32)
    response.set_cookie(
        COOKIE, titular, httponly=True, secure=request.app.state.secure_cookie, samesite="strict"
    )
    return demo.gerar(titular, boleto)


@router.get("/boletos/status/erro", response_model=list[BoletoResponse])
def listar_boletos_com_erro(request: Request):
    demo = request.app.state.demo
    if demo is not None:
        return demo.listar_erros(sessao(request))
    return boleto_service.listar_erros()


@router.get("/boletos/{codigo}", response_model=BoletoResponse)
def reemitir_boleto(codigo: str, request: Request):
    return buscar(request, codigo)


@router.get("/boletos/{codigo}/pdf")
def gerar_pdf(codigo: str, request: Request):
    boleto = buscar(request, codigo)
    return Response(
        content=gerar_pdf_boleto(boleto),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="boleto-simulado.pdf"'},
    )


@router.post("/boletos/{codigo}/reprocessar")
def reprocessar_boleto(codigo: str, request: Request):
    demo = request.app.state.demo
    if demo is not None:
        demo.reprocessar(sessao(request), codigo)
    else:
        boleto_service.solicitar_reprocessamento(codigo)
    return {"mensagem": "Boleto enviado para reprocessamento"}
