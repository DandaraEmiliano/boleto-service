from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from app.schema.boleto import BoletoResponse


def gerar_pdf_boleto(boleto: BoletoResponse) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("Boleto simulado | Boleto Service")
    pdf.setFillColor(HexColor("#12342a"))
    pdf.rect(0, 676, A4[0], 166, fill=1, stroke=0)
    pdf.setFillColor(HexColor("#e9f7ec"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawString(56, 760, "Boleto simulado")
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(56, 722, "DEMONSTRAÇÃO • SEM VALOR PARA PAGAMENTO")

    pdf.setFillColor(HexColor("#172d26"))
    valor = f"{boleto.valor:,.2f}".translate(str.maketrans(",.", ".,"))
    campos = (
        ("Pagador", boleto.nome),
        ("Valor", f"R$ {valor}"),
        ("Vencimento", boleto.vencimento.strftime("%d/%m/%Y")),
        ("Código de consulta", boleto.codigo),
        ("Linha demonstrativa", boleto.linha_digitavel),
    )
    y = 627
    for rotulo, conteudo in campos:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(56, y, rotulo)
        pdf.setFont("Helvetica", 14)
        for linha in simpleSplit(conteudo, "Helvetica", 14, A4[0] - 112):
            y -= 20
            pdf.drawString(56, y, linha)
        y -= 36
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
