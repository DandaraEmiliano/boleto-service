from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BoletoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str = Field(pattern=r"^(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})$")
    valor: Decimal = Field(gt=0, le=Decimal("9999999.99"), decimal_places=2)
    vencimento: date


class BoletoResponse(BaseModel):
    nome: str
    cpf: str
    valor: float
    vencimento: date
    codigo: str
    linha_digitavel: str
    status: str
