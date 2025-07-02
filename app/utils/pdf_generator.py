from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def gerar_pdf_boleto(boleto: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)

    y = 800
    pdf.drawString(100, y, "BOLETO BANCÁRIO")
    y -= 30
    for key, value in boleto.items():
        pdf.drawString(100, y, f"{key.capitalize()}: {value}")
        y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()
