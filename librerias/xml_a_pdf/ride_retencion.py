from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from librerias.xml_a_pdf.constantes import *
from librerias.diccionarios import ambiente, tipo_emision, nombre_impuesto_retencion, nombres_comprobantes_excel
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from librerias.xml_a_pdf.funciones_auxiliares import dividir_y_centrar_texto, es_agente_retencion, es_gran_contribuyente


def datos_emisor_ret(pdf, ult_x, ult_y, datos_retencion, ruta):
    # Nos separamos de los bordes
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    # tamaño ancho pagina menos los 4 espaciados de bloques
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 4) / 2
    img_x = ancho_bloque
    # 1.8 Es la relacion de aspecto de la imagen
    img_y = float(img_x / 2.5)
    # Dibujamos el logo de la empresa.
    pdf.drawImage(ruta, x * mm, (y - img_y) * mm, width=img_x * mm, height=img_y * mm, mask='auto')
    # Metemos el logo dentro de un rectangulo
    pdf.roundRect(x * mm, (y - img_y) * mm, img_x * mm, img_y * mm, 5, stroke=1, fill=0)
    # Espaciamos restando el tamaño de la imagen mas el espaciado de bloques
    y -= img_y + ESPACIADO_BLOQUES_RIDE

    # Capturamos Y para ver donde empieza y luego capturamos donde termina para saber el alto del bloque
    alto_bloque = y
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.setFillColorRGB(0, 0, 1)
    # Escribimos la razon social.
    y -= dividir_y_centrar_texto(pdf, datos_retencion["infoTributaria"]["razonSocial"], y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    # Espaciamos
    # Obtenemos nueva X centrada para el bloque.
    y -= dividir_y_centrar_texto(pdf, datos_retencion["infoTributaria"].get("nombreComercial",
                                                                          datos_retencion["infoTributaria"][
                                                                              "razonSocial"]), y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_10)
    pdf.setFillColorRGB(0, 0, 0)
    # Espaciamos
    y -= dividir_y_centrar_texto(pdf, f'DIRECCIÓN MATRIZ: {datos_retencion["infoTributaria"]["dirMatriz"]}', y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'DIRECCIÓN SUCURSAL: {datos_retencion["infoTributaria"]["dirMatriz"]}', y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'Contribuyente Especial: {datos_retencion["infoCompRetencion"].get("contribuyenteEspecial", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'Obligado A Llevar Contabilidad: {datos_retencion["infoCompRetencion"].get("obligadoContabilidad", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_agente_retencion = 'Agente de Retención: SI' if es_agente_retencion(datos_retencion) else 'Agente de Retención: NO'
    y -= dividir_y_centrar_texto(pdf, texto_agente_retencion, y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_gran_contribuyente = 'Gran Contribuyente: SI' if es_gran_contribuyente(datos_retencion) else 'Gran Contribuyente: NO'
    y -= dividir_y_centrar_texto(pdf, texto_gran_contribuyente, y, x, ancho_bloque, "Helvetica", TAM_6)
    # El alto del bloque es al anterior alto del bloque menos lo posicion actual de Y
    alto_bloque -= y
    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    # Seteamos las coordenadas donde empezara el siguiente bloque.
    # Pasamos el ancho mas el espaciado, que es lo que se ha tomado el ancho del bloque.
    return (ancho_bloque + ESPACIADO_BLOQUES_RIDE * 2), y


def detalle_ret(pdf, ult_x, ult_y, datos_retencion):
    # La ult_x es el ancho del bloque izq mas el espaciado, asi que le agrego el propio de este bloque.
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Como empezamos de arriba usamos el alto de la pagina.
    y = ALTO_A4 - ESPACIADO_BLOQUES_RIDE
    # Traemos del bloque del lado izquiero el alto para igualarlo al de este bloque a la derecha
    alto_bloque = y
    # Tamaño ancho pagina menos el contenido del bloque contiguo menos el margen de los bordes
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 4) / 2

    # Nos separamos del borde superior
    y -= ESPACIADO_CONTENIDO_RIDE * 2
    y -= dividir_y_centrar_texto(pdf, f'RUC:  {datos_retencion["infoTributaria"]["ruc"]}', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_14) * 2
    y -= dividir_y_centrar_texto(pdf, f'RETENCIÓN', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de Rojo
    pdf.setFillColorRGB(1, 0, 0)
    y -= dividir_y_centrar_texto(pdf,
                                 f'No. {datos_retencion["infoTributaria"]["estab"]}-{datos_retencion["infoTributaria"]["ptoEmi"]}-{datos_retencion["infoTributaria"]["secuencial"]}',
                                 y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de negro
    pdf.setFillColorRGB(0, 0, 0)
    y -= dividir_y_centrar_texto(pdf, 'NÚMERO DE AUTORIZACIÓN', y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    y -= dividir_y_centrar_texto(pdf, datos_retencion["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'FECHA Y HORA DE AUTORIZACIÓN: ', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, datos_retencion["datos_extras"]["fechaAutorizacion"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'AMBIENTE: {ambiente.get(datos_retencion["infoTributaria"].get("ambiente", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'TIPO EMISIÓN: {tipo_emision.get(datos_retencion["infoTributaria"].get("tipoEmision", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'CLAVE DE ACCESO', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= 8
    # Escribimos el codigo de barras y el numero de autorizacion centrada.
    barcode = code128.Code128(datos_retencion["infoTributaria"]["claveAcceso"], barHeight=10 * mm, barWidth=0.2565 * mm)
    gap = barcode.width / mm
    newx = x + (ancho_bloque / 2.0) - (gap / 2)
    barcode.drawOn(pdf, newx * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    y -= dividir_y_centrar_texto(pdf, datos_retencion["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    # La funcion de dividir y centrar texto ya trae el espaciado por defecto, pero para cuadrar con el bloque de la
    # izquierda tenemos esta magia de aca.
    y -= ESPACIADO_CONTENIDO_RIDE / 1.5
    # El alto del bloque es al anterior alto del bloque menos lo posicion actual de Y
    alto_bloque -= y
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    # Seteamos las coordenadas donde empezara el siguiente bloque.
    x = 0
    return x, y


def datos_cliente_ret(pdf, ult_x, ult_y, datos_retencion):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE
    alto_bloque = y
    y -= ESPACIADO_CONTENIDO_RIDE
    # tamaño ancho pagina menos los bordes del PDF
    ancho_bloque = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2
    # Seteamos fuente y tamano
    pdf.setFont("Helvetica", TAM_8)
    # Escribimos la razon social
    pdf.drawString((x + 3) * mm, y * mm,
                   f'RAZÓN SOCIAL/NOMBRES Y APELLIDOS: {datos_retencion["infoCompRetencion"]["razonSocialSujetoRetenido"]}')
    y -= ESPACIADO_CONTENIDO_RIDE * 1.5
    # Seteamos fuente y tamano
    pdf.setFont("Helvetica", TAM_8)
    # Escribimos la razon social
    pdf.drawString((x + 3) * mm, y * mm,
                   f'FECHA EMISIÓN: {datos_retencion["infoCompRetencion"]["fechaEmision"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    # ancho del bloque el inicial y menos el actual
    alto_bloque -= y
    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)

    return 0, y


def contenido_ret(pdf, ult_x, ult_y, detalles):
    retenciones = detalles['impuestos']
    periodo_fiscal = detalles['infoCompRetencion']['periodoFiscal']
    fecha_emision_default = detalles['infoCompRetencion']['fechaEmision']
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    ancho_bloque = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2
    p8_center = ParagraphStyle('parrafos',
                               fontSize=8,
                               fontName="Helvetica", alignment=TA_CENTER)
    data = [[Paragraph('Comprobante', p8_center), Paragraph('Numero Comprobante', p8_center),
             Paragraph('Fecha Emisión', p8_center), Paragraph('Ejercicio Fiscal', p8_center),
             Paragraph('Base   Retención', p8_center), Paragraph('Impuesto', p8_center), Paragraph('Cod. Impuesto', p8_center),
             Paragraph('% Reten.', p8_center), Paragraph('Valor Retenido', p8_center)]]

    for retencion in retenciones:
        # CONFORME TABLA 30
        comprobante = nombres_comprobantes_excel.get(retencion.get('codDocSustento', ''), 'Otros')
        referencia = retencion.get('numDocSustento', '000-000-000000000')
        fecha_emision = retencion.get('fechaEmisionDocSustento', fecha_emision_default)
        base_imponible = retencion.get('baseImponible', 'N/A')
        tipo_impuesto = nombre_impuesto_retencion.get(retencion.get('codigo', ''), 'N/A')
        codigo_impuesto = retencion.get('codigoRetencion', 'N/A')
        porcentaje_ret = retencion.get('porcentajeRetener', 'N/A')
        valor_retenido = retencion.get('valorRetenido', 'N/A')
        data.append(
            [Paragraph(comprobante, p8_center), Paragraph(referencia, p8_center), Paragraph(fecha_emision, p8_center),
             Paragraph(periodo_fiscal, p8_center), Paragraph(base_imponible, p8_center),
             Paragraph(tipo_impuesto, p8_center), Paragraph(codigo_impuesto, p8_center),
             Paragraph(porcentaje_ret, p8_center), Paragraph(valor_retenido, p8_center)])
    col_width = (ancho_bloque / float(12))
    tabla_contenido = Table(data,
                            colWidths=[col_width * 2 * mm, col_width * 2 * mm, col_width * 2 * mm, col_width * mm,
                                       col_width * mm, col_width * mm, col_width * mm,
                                       col_width * mm, col_width * mm])
    tabla_contenido.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    tabla_contenido.wrapOn(pdf, 500, 500)
    w, h = tabla_contenido.wrap(0, 0)
    alto_tabla = h / mm
    tabla_contenido.drawOn(pdf, x * mm, (y - alto_tabla) * mm)

    y -= alto_tabla + ESPACIADO_BLOQUES_RIDE

    return 0, y


def inf_adicional_ret(pdf, ult_x, ult_y, datos_retencion):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE
    alto_bloque = y
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2)
    y -= ESPACIADO_CONTENIDO_RIDE * 1.5
    y -= dividir_y_centrar_texto(pdf, "INFORMACIÓN ADICIONAL", y, x, ancho_bloque, "Helvetica-Bold", TAM_14)
    y += ESPACIADO_CONTENIDO_RIDE / 1.5
    pdf.line(x * mm, y * mm, (x + ancho_bloque) * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.setFont("Helvetica", TAM_8)

    for item in datos_retencion:
        for clave, valor in item.items():
            texto = f'{clave}:  {valor}'
            texto_cortado = texto
            pdf.drawString((x + 2) * mm, y * mm, texto_cortado)
            y -= ESPACIADO_CONTENIDO_RIDE  # Ajustar y para la siguiente línea
    alto_bloque -= y
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    return y


# Funcion que retorna el archivo con el pdf de la factura para enviar por correo.
def imprimir_retencion_pdf(documento, ruta_archivo, ruta_logo):
    # Creo el canvas y le paso el buffer.
    p = canvas.Canvas(ruta_archivo, pagesize=A4)
    # El ult_y lo coloco directamente como ALTO_A4, ya que inicio desde la parte de arriba.
    ult_x, ult_y = datos_emisor_ret(p, 0, ALTO_A4, documento, ruta_logo)
    detalle_ret(p, ult_x, ALTO_A4, documento)
    ult_x, ult_y = datos_cliente_ret(p, 0, ult_y, documento)
    ult_x, ult_y = contenido_ret(p, ult_x, ult_y, documento)
    inf_adicional_ret(p, ult_x, ult_y, documento['infoAdicional'])
    p.showPage()
    p.save()