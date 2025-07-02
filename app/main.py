from fastapi import FastAPI
from app.api import boleto


app = FastAPI(
    title="Boleto Service",
    description="API for generating boletos",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(boleto.router)
