from pydantic import BaseModel, Field
from datetime import date

class BoletoCreate(BaseModel):
    nome: str
    cpf: str
    valor: float
    vencimento: date

class BoletoResponse(BaseModel):
    nome: str
    cpf: str
    valor: float
    vencimento: date
    codigo: str
    linha_digitavel: str
