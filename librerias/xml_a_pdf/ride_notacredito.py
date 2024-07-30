from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from librerias.xml_a_pdf.constantes import *
from librerias.diccionarios import ambiente, tipo_emision, nombres_comprobantes_excel
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from librerias.xml_a_pdf.funciones_auxiliares import dividir_y_centrar_texto, es_gran_contribuyente, es_agente_retencion


def datos_emisor_nc(pdf, ult_x, ult_y, datos_nc, ruta):
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
    y -= dividir_y_centrar_texto(pdf, datos_nc["infoTributaria"]["razonSocial"], y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    # Espaciamos
    # Obtenemos nueva X centrada para el bloque.
    y -= dividir_y_centrar_texto(pdf, datos_nc["infoTributaria"].get("nombreComercial", datos_nc["infoTributaria"]["razonSocial"]), y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    pdf.setFillColorRGB(0, 0, 0)
    # Espaciamos
    y -= dividir_y_centrar_texto(pdf, f'DIRECCIÓN MATRIZ: {datos_nc["infoTributaria"]["dirMatriz"]}', y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'DIRECCIÓN SUCURSAL: {datos_nc["infoTributaria"]["dirMatriz"]}', y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'Contribuyente Especial: {datos_nc["infoNotaCredito"].get("contribuyenteEspecial", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf, f'Obligado A Llevar Contabilidad: {datos_nc["infoNotaCredito"].get("obligadoContabilidad", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf,
                                 f'Regimen Microempresa: {datos_nc["infoTributaria"].get("regimenMicroempresa", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_agente_retencion = 'Agente de Retención: SI' if es_agente_retencion(datos_nc) else 'Agente de Retención: NO'
    y -= dividir_y_centrar_texto(pdf, texto_agente_retencion, y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_gran_contribuyente = 'Gran Contribuyente: SI' if es_gran_contribuyente(datos_nc) else 'Gran Contribuyente: NO'
    y -= dividir_y_centrar_texto(pdf, texto_gran_contribuyente, y, x, ancho_bloque, "Helvetica", TAM_6)
    # El alto del bloque es al anterior alto del bloque menos lo posicion actual de Y
    alto_bloque -= y
    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    # Seteamos las coordenadas donde empezara el siguiente bloque.
    # Pasamos el ancho mas el espaciado, que es lo que se ha tomado el ancho del bloque.
    return (ancho_bloque + ESPACIADO_BLOQUES_RIDE * 2), y


def detalle_nc(pdf, ult_x, ult_y, datos_nc):
    # La ult_x es el ancho del bloque izq mas el espaciado, asi que le agrego el propio de este bloque.
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Como empezamos de arriba usamos el alto de la pagina.
    y = ALTO_A4
    # Traemos del bloque del lado izquiero el alto para igualarlo al de este bloque a la derecha
    alto_bloque_izq = ALTO_A4 - ult_y - ESPACIADO_BLOQUES_RIDE
    # Tamaño ancho pagina menos el contenido del bloque contiguo menos el margen de los bordes
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 4) / 2

    # Nos separamos del borde superior
    y -= ESPACIADO_BLOQUES_RIDE + ESPACIADO_CONTENIDO_RIDE * 2
    y -= dividir_y_centrar_texto(pdf, f'RUC:  {datos_nc["infoTributaria"]["ruc"]}', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_14) * 2
    y -= dividir_y_centrar_texto(pdf, f'NOTA DE CREDITO', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de Rojo
    pdf.setFillColorRGB(1, 0, 0)
    y -= dividir_y_centrar_texto(pdf,
                                 f'No. {datos_nc["infoTributaria"]["estab"]}-{datos_nc["infoTributaria"]["ptoEmi"]}-{datos_nc["infoTributaria"]["secuencial"]}',
                                 y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de negro
    pdf.setFillColorRGB(0, 0, 0)
    y -= dividir_y_centrar_texto(pdf, 'NÚMERO DE AUTORIZACIÓN', y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    y -= dividir_y_centrar_texto(pdf, datos_nc["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'FECHA Y HORA DE AUTORIZACIÓN: ', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, datos_nc["datos_extras"]["fechaAutorizacion"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'AMBIENTE: {ambiente.get(datos_nc["infoTributaria"].get("ambiente", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'TIPO EMISIÓN: {tipo_emision.get(datos_nc["infoTributaria"].get("tipoEmision", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'CLAVE DE ACCESO', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= 8
    # Escribimos el codigo de barras y el numero de autorizacion centrada.
    barcode = code128.Code128(datos_nc["infoTributaria"]["claveAcceso"], barHeight=10 * mm, barWidth=0.2565 * mm)
    gap = barcode.width / mm
    newx = x + (ancho_bloque / 2.0) - (gap / 2)
    barcode.drawOn(pdf, newx * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    y -= dividir_y_centrar_texto(pdf, datos_nc["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    pdf.roundRect(x * mm, ult_y * mm, ancho_bloque * mm, alto_bloque_izq * mm, 5, stroke=1, fill=0)
    # Seteamos las coordenadas donde empezara el siguiente bloque.
    x = 0
    return x, y


def datos_cliente_nc(pdf, ult_x, ult_y, datos_nc):
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
                   f'RAZÓN SOCIAL/NOMBRES Y APELLIDOS: {datos_nc["infoNotaCredito"]["razonSocialComprador"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.drawString((x + 3) * mm, y * mm,
                   f'IDENTIFICACIÓN: {datos_nc["infoNotaCredito"]["identificacionComprador"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    # Escribimos la razon social
    pdf.drawString((x + 3) * mm, y * mm,
                   f'FECHA EMISIÓN: {datos_nc["infoNotaCredito"]["fechaEmision"]}')
    y -= ESPACIADO_CONTENIDO_RIDE / 2
    pdf.line(x * mm, y * mm, (x + ancho_bloque) * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.drawString((x + 3) * mm, y * mm,
                   f'COMPROBANTE QUE SE MODIFICA: {nombres_comprobantes_excel.get(datos_nc["infoNotaCredito"].get("codDocModificado", "0"), "DESCONOCIDO")} - {datos_nc["infoNotaCredito"]["numDocModificado"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.drawString((x + 3) * mm, y * mm,
                   f'FECHA EMISIÓN (COMPROBANTE A MODIFICAR): {datos_nc["infoNotaCredito"]["fechaEmisionDocSustento"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.drawString((x + 3) * mm, y * mm,
                   f'RAZÓN DE MODIFICACIÓN: {datos_nc["infoNotaCredito"]["motivo"]}')
    y -= ESPACIADO_CONTENIDO_RIDE
    # ancho del bloque el inicial y menos el actual
    alto_bloque -= y
    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)

    return 0, y


def contenido_nc(pdf, ult_x, ult_y, detalles):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    ancho_bloque = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2
    p8_center = ParagraphStyle('parrafos', fontSize=8, fontName="Helvetica", alignment=TA_CENTER)
    p8_right = ParagraphStyle('parrafos', fontSize=8, fontName="Helvetica", alignment=TA_RIGHT)
    data = []
    data.append([Paragraph('Cod. Principal', p8_center),
                 Paragraph('Cod. Auxiliar', p8_center),
                 Paragraph('Descripción', p8_center),
                 Paragraph('#', p8_center),
                 Paragraph('Precio Uni.', p8_center),
                 Paragraph('Desc.', p8_center),
                 Paragraph('Precio Tot.', p8_center)])

    for detalle in detalles:
        # Extracción de los campos requeridos del detalle
        codigo_principal = detalle.get('codigoPrincipal') or detalle.get('codigoInterno', '')
        codigo_auxiliar = detalle.get('codigoAuxiliar') or detalle.get('codigoAdicional', '')
        descripcion = detalle['descripcion'] + (' -**- ' + detalle.get('marcaProducto', '') if detalle.get('marcaProducto') else '')
        detalle.get('codigoAuxiliar') or detalle.get('codigoAdicional', '')
        # Formatear los valores numéricos
        cantidad = int(float(detalle['cantidad']))  # Convertir a entero
        precio_unitario = '{:.3f}'.format(float(detalle['precioUnitario']))
        descuento = '{:.3f}'.format(float(detalle.get('descuento', '0.00')))
        precio_total_sin_impuesto = '{:.3f}'.format(float(detalle['precioTotalSinImpuesto']))
        # Agregar los valores formateados a la lista 'data'
        data.append([
            Paragraph(codigo_principal, p8_center),
            Paragraph(codigo_auxiliar, p8_center),
            Paragraph(descripcion, p8_center),
            Paragraph(str(cantidad), p8_center),  # Convertir cantidad a cadena
            Paragraph(precio_unitario, p8_right),
            Paragraph(descuento, p8_right),
            Paragraph(precio_total_sin_impuesto, p8_right)
        ])
    col_width = (ancho_bloque / float(22))
    tabla_contenido = Table(data,
                            colWidths=[col_width * 3 * mm, col_width * 3 * mm, col_width * 8 * mm,
                                       col_width * 2 * mm,
                                       col_width * 2 * mm, col_width * 2 * mm, col_width * 2 * mm])
    tabla_contenido.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    tabla_contenido.wrapOn(pdf, 500, 500)
    w, h = tabla_contenido.wrap(0, 0)
    alto_tabla = h / mm
    tabla_contenido.drawOn(pdf, x * mm, (y - alto_tabla) * mm)
    y -= alto_tabla
    return y


def inf_adicional_nc(pdf, ult_x, ult_y, datos_nc):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE
    alto_bloque = y
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2) / 1.5
    y -= ESPACIADO_CONTENIDO_RIDE * 1.5
    y -= dividir_y_centrar_texto(pdf, "INFORMACIÓN ADICIONAL", y, x, ancho_bloque, "Helvetica-Bold", TAM_14)
    y += ESPACIADO_CONTENIDO_RIDE / 1.5
    pdf.line(x * mm, y * mm, (x + ancho_bloque) * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    pdf.setFont("Helvetica", TAM_8)

    for item in datos_nc:
        for clave, valor in item.items():
            texto = f'{clave}:  {valor}'
            texto_cortado = texto[:75]  # Limitar la longitud del texto a 110 caracteres
            pdf.drawString((x + 2) * mm, y * mm, texto_cortado)
            y -= ESPACIADO_CONTENIDO_RIDE  # Ajustar y para la siguiente línea
    alto_bloque -= y
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    return y


def totales_nc(pdf, ult_x, ult_y, datos):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    ancho_bloque_ant = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2) / 1.5
    # ESTO NO LO VES NI EN LA NASA
    tam_col_izq = pdf.stringWidth('Subtotal no Objeto de IVA            ', "Helvetica", 8) / mm
    tam_col_der = ANCHO_A4 - ancho_bloque_ant - tam_col_izq - ESPACIADO_BLOQUES_RIDE * 3

    p8 = ParagraphStyle('parrafos', fontSize=TAM_8, fontName="Helvetica")
    p8_right = ParagraphStyle('parrafos', fontSize=TAM_8, fontName="Helvetica", alignment=TA_RIGHT)

    # Convertir valores numéricos a cadenas de texto
    subtotal_sin_imp = '{:.2f}'.format(datos['SUBTOTAL SIN IMPUESTOS'])
    subtotal_12 = '{:.2f}'.format(datos['SUBTOTAL 12%'])
    subtotal_0 = '{:.2f}'.format(datos['SUBTOTAL 0%'])
    subtotal_no_iva = '{:.2f}'.format(datos['Subtotal No Objeto de IVA'])
    subtotal_exc_iva = '{:.2f}'.format(datos['Subtotal Exento de IVA'])
    total_descuento = '{:.2f}'.format(datos['DESCUENTO'])
    ICE = '{:.2f}'.format(datos['ICE'])
    IVA_12 = '{:.2f}'.format(datos['IVA 12%'])
    IRBPNR = '{:.2f}'.format(datos['IRBPNR'])
    PROPINA = '{:.2f}'.format(datos['PROPINA'])
    total = '{:.2f}'.format(datos['TOTAL'])

    data = [[Paragraph('SUBTOTAL SIN IMPUESTOS', p8), Paragraph(subtotal_sin_imp, p8_right)],
            [Paragraph('SUBTOTAL 12%', p8), Paragraph(subtotal_12, p8_right)],
            [Paragraph('SUBTOTAL 0%', p8), Paragraph(subtotal_0, p8_right)],
            [Paragraph('Subtotal No Objeto de IVA', p8), Paragraph(subtotal_no_iva, p8_right)],
            [Paragraph('Subtotal Exento de IVA', p8), Paragraph(subtotal_exc_iva, p8_right)],
            [Paragraph('TOTAL DESCUENTO', p8), Paragraph(total_descuento, p8_right)],
            [Paragraph('ICE', p8), Paragraph(ICE, p8_right)],
            [Paragraph('IVA 12%', p8), Paragraph(IVA_12, p8_right)],
            [Paragraph('IRBPNR', p8), Paragraph(IRBPNR, p8_right)],
            [Paragraph('PROPINA', p8), Paragraph(PROPINA, p8_right)],
            [Paragraph('VALOR TOTAL', p8), Paragraph(total, p8_right)],
            ]
    tabla_totales = Table(data, colWidths=(tam_col_izq * mm, tam_col_der * mm))
    tabla_totales.setStyle(TableStyle([('ALIGN', (1, 0), (0, 0), 'LEFT'),
                                       ('ALIGN', (-1, 0), (0, -1), 'RIGHT'),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                       ]))
    w, h = tabla_totales.wrap(0, 0)
    tabla_totales.drawOn(pdf, (x + ancho_bloque_ant + ESPACIADO_BLOQUES_RIDE) * mm, y * mm - h)


def calcular_totales_nc(datos_factura):
    subtotal_0 = subtotal_12 = subtotal_no_sujeto = subtotal_exento = ice = iva_12 = irbpnr = 0.0

    for impuesto in datos_factura['infoNotaCredito']['totalConImpuestos']:
        base_imponible = float(impuesto['baseImponible'])
        valor = float(impuesto['valor'])
        codigo_porcentaje = impuesto['codigoPorcentaje']

        if impuesto['codigo'] == '2':  # IVA
            if codigo_porcentaje == '0':
                subtotal_0 += base_imponible
            elif codigo_porcentaje == '2':
                subtotal_12 += base_imponible
                iva_12 += valor
            elif codigo_porcentaje == '6':
                subtotal_no_sujeto += base_imponible
            elif codigo_porcentaje == '7':
                subtotal_exento += base_imponible

        elif impuesto['codigo'] == '3':  # ICE
            ice += valor

        elif impuesto['codigo'] == '5':  # IRBPNR
            irbpnr += valor

    subtotal_sin_impuestos = float(datos_factura['infoNotaCredito']['totalSinImpuestos'])
    descuento = float(datos_factura['infoNotaCredito'].get('totalDescuento', 0))
    propina = float(datos_factura['infoNotaCredito'].get('propina', 0))
    importe_total = float(datos_factura['infoNotaCredito'].get('importeTotal', 0))
    # Si importe total no está presente o es 0.00, calcularlo
    if importe_total == 0.00:
        importe_total = subtotal_sin_impuestos + iva_12 + irbpnr + ice + propina - descuento

    return {
        'SUBTOTAL SIN IMPUESTOS': subtotal_sin_impuestos,
        'SUBTOTAL 12%': subtotal_12,
        'SUBTOTAL 0%': subtotal_0,
        'Subtotal No Objeto de IVA': subtotal_no_sujeto,
        'Subtotal Exento de IVA': subtotal_exento,
        'DESCUENTO': descuento,
        'ICE': ice,
        'IRBPNR': irbpnr,
        'IVA 12%': iva_12,
        'PROPINA': propina,
        'TOTAL': importe_total
    }


# Funcion que retorna el archivo con el pdf de la factura para enviar por correo.
def imprimir_nc_pdf(documento, ruta_archivo, ruta_logo):
    # Creo el canvas y le paso el buffer.
    p = canvas.Canvas(ruta_archivo, pagesize=A4)
    # Ubico el inicio de las cordenadas en la esquina superior izquierda
    ult_y = ALTO_A4
    # Empiezo a agregar las partes modularmente de izquierda a derecha de arriba abajo.
    ult_x, ult_y = datos_emisor_nc(p, 0, ult_y, documento, ruta_logo)
    temp_y = ult_y
    ult_x, ult_y = detalle_nc(p, ult_x, ult_y, documento)
    ult_x, ult_y = datos_cliente_nc(p, ult_x, temp_y, documento)
    ult_y = contenido_nc(p, ult_x, ult_y, documento['detalles'])
    totales_nc(p, 0, ult_y, calcular_totales_nc(documento))
    inf_adicional_nc(p, 0, ult_y, documento['infoAdicional'])
    p.showPage()
    p.save()