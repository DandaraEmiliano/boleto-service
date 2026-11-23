from collections import OrderedDict
from threading import Lock
from time import monotonic

from app.schema.boleto import BoletoCreate, BoletoResponse
from app.services.boleto_service import BoletoForaDeEstado, BoletoNaoEncontrado, novo_boleto

PAGADORES_DEMO = {
    "Marina Exemplo": "00000000000",
    "Rafael Exemplo": "11111111111",
    "Clara Exemplo": "22222222222",
}


class DemoBoletos:
    def __init__(self):
        self._registros: OrderedDict[str, tuple[str, BoletoResponse, float]] = OrderedDict()
        self._lock = Lock()

    def gerar(self, sessao: str, dados: BoletoCreate) -> BoletoResponse:
        boleto = novo_boleto(dados)
        with self._lock:
            if len(self._registros) >= 2000:
                self._registros.popitem(last=False)
            self._registros[boleto.codigo] = (sessao, boleto, 0)
        return boleto.model_copy()

    def buscar(self, sessao: str | None, codigo: str) -> BoletoResponse:
        with self._lock:
            boleto, _ = self._buscar(sessao, codigo)
            return boleto.model_copy()

    def listar_erros(self, sessao: str | None) -> list[BoletoResponse]:
        with self._lock:
            return [
                boleto.model_copy()
                for titular, boleto, _ in reversed(self._registros.values())
                if titular == sessao and boleto.status == "erro"
            ]

    def reprocessar(self, sessao: str | None, codigo: str) -> None:
        with self._lock:
            boleto, titular = self._buscar(sessao, codigo)
            if boleto.status != "erro":
                raise BoletoForaDeEstado
            boleto.status = "reprocessando"
            self._registros[codigo] = (titular, boleto, monotonic() + 1.2)

    def _buscar(self, sessao: str | None, codigo: str) -> tuple[BoletoResponse, str]:
        registro = self._registros.get(codigo)
        if registro is None or registro[0] != sessao:
            raise BoletoNaoEncontrado
        titular, boleto, concluir_em = registro
        if boleto.status == "reprocessando" and monotonic() >= concluir_em:
            boleto.status = "enviado"
        return boleto, titular
