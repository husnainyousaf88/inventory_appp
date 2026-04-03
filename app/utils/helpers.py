from reportlab.graphics.barcode import createBarcodeDrawing

def barcode_drawing(value):
    return createBarcodeDrawing(
        'Code128',
        value=value,
        barHeight=20,
        barWidth=1,
        humanReadable=True  # shows text under barcode
    )