from os import getenv
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo.errors import PyMongoError

from app.api import boleto
from app.services.boleto_service import BoletoForaDeEstado, BoletoNaoEncontrado
from app.services.demo import DemoBoletos, PAGADORES_DEMO

WEB = Path(__file__).resolve().parent.parent / "web"


def create_app(demo_mode: bool = False, secure_cookie: bool = False) -> FastAPI:
    app = FastAPI(
        title="Boleto Service",
        description="Emissão e reprocessamento de boletos simulados",
        version="2.0.0",
    )
    app.state.demo = DemoBoletos() if demo_mode else None
    app.state.secure_cookie = secure_cookie

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/config")
    def config():
        return {"demo": demo_mode, "pagadores": PAGADORES_DEMO if demo_mode else {}}

    @app.get("/", include_in_schema=False)
    def frontend():
        return FileResponse(WEB / "index.html")

    @app.middleware("http")
    async def cache_privacy(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/boletos"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(BoletoNaoEncontrado)
    async def nao_encontrado(_request, _exc):
        return JSONResponse(status_code=404, content={"detail": "Boleto não encontrado"})

    @app.exception_handler(BoletoForaDeEstado)
    async def estado_invalido(_request, _exc):
        return JSONResponse(status_code=400, content={"detail": "Boleto não está com status de erro"})

    @app.exception_handler(PyMongoError)
    async def mongo_indisponivel(_request, _exc):
        return JSONResponse(status_code=503, content={"detail": "Persistência indisponível. Tente novamente."})

    app.include_router(boleto.router)
    app.mount("/assets", StaticFiles(directory=WEB), name="assets")
    return app


app = create_app(
    demo_mode=getenv("BOLETO_DEMO") == "1",
    secure_cookie=getenv("BOLETO_SECURE_COOKIE") == "1",
)
