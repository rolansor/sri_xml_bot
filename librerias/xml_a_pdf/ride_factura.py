import math
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from librerias.xml_a_pdf.constantes import *
from librerias.diccionarios import ambiente, tipo_emision, nombres_formapago
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128,code93
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from librerias.xml_a_pdf.funciones_auxiliares import dividir_y_centrar_texto, es_gran_contribuyente, es_agente_retencion


def datos_emisor_fac(pdf, ult_x, ult_y, datos_factura, ruta):
    # Nos separamos de los bordes
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    # tamaño ancho pagina menos los 4 espaciados de bloques
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 4) / 2
    img_x = ancho_bloque
    # 2.5 Es la relacion de aspecto de la imagen, modificada para tener mas espacio en la factura.
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
    # Escribimos el nombre comercial
    y -= dividir_y_centrar_texto(pdf, datos_factura["infoTributaria"]["razonSocial"], y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_10)
    y -= dividir_y_centrar_texto(pdf, datos_factura["infoTributaria"].get("nombreComercial",
                                                                          datos_factura["infoTributaria"][
                                                                              "razonSocial"]), y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_10)
    pdf.setFillColorRGB(0, 0, 0)
    y -= dividir_y_centrar_texto(pdf, f'DIRECCIÓN MATRIZ: {datos_factura["infoTributaria"]["dirMatriz"]}', y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf,
                                 f'DIRECCIÓN SUCURSAL: {datos_factura["infoTributaria"].get("dirEstablecimiento", datos_factura["infoTributaria"]["dirMatriz"])}',
                                 y, x,
                                 ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf,
                                 f'Contribuyente Especial: {datos_factura["infoFactura"].get("contribuyenteEspecial", "N/A")}  ---  Obligado A Llevar Contabilidad: {datos_factura["infoFactura"].get("obligadoContabilidad", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    y -= dividir_y_centrar_texto(pdf,
                                 f'Regimen Microempresa: {datos_factura["infoTributaria"].get("regimenMicroempresa", "N/A")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_agente_retencion = 'Agente de Retención: SI' if es_agente_retencion(datos_factura) else 'Agente de Retención: NO'
    y -= dividir_y_centrar_texto(pdf, texto_agente_retencion, y, x, ancho_bloque, "Helvetica", TAM_6)
    texto_gran_contribuyente = 'Gran Contribuyente: SI' if es_gran_contribuyente(datos_factura) else 'Gran Contribuyente: NO'
    y -= dividir_y_centrar_texto(pdf, texto_gran_contribuyente, y, x, ancho_bloque, "Helvetica", TAM_6)
    # El alto del bloque es al anterior alto del bloque menos lo posicion actual de Y
    alto_bloque -= y
    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    # -roundRect(x, y, ancho, alto, radio de curva, stroke, fill)
    # stroke y fill, si es 0 inidica no mostrar trazo ni relleno
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    # Seteamos las coordenadas donde empezara el siguiente bloque.
    # Pasamos el ancho mas el espaciado, que es lo que se ha tomado el ancho del bloque.
    return (ancho_bloque + ESPACIADO_BLOQUES_RIDE * 2), y


def detalle_fac(pdf, ult_x, ult_y, datos_factura):
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
    y -= dividir_y_centrar_texto(pdf, f'RUC:  {datos_factura["infoTributaria"]["ruc"]}', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_14) * 2
    y -= dividir_y_centrar_texto(pdf, f'FACTURA', y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de Rojo
    pdf.setFillColorRGB(1, 0, 0)
    y -= dividir_y_centrar_texto(pdf,
                                 f'No. {datos_factura["infoTributaria"]["estab"]}-{datos_factura["infoTributaria"]["ptoEmi"]}-{datos_factura["infoTributaria"]["secuencial"]}',
                                 y, x, ancho_bloque,
                                 "Helvetica-Bold", TAM_18) * 2
    # Pintamos de negro
    pdf.setFillColorRGB(0, 0, 0)
    y -= dividir_y_centrar_texto(pdf, 'NÚMERO DE AUTORIZACIÓN', y, x, ancho_bloque, "Helvetica-Bold", TAM_10)
    y -= dividir_y_centrar_texto(pdf, datos_factura["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'FECHA Y HORA DE AUTORIZACIÓN: ', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, datos_factura["datos_extras"]["fechaAutorizacion"], y, x, ancho_bloque,
                                 "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'AMBIENTE: {ambiente.get(datos_factura["infoTributaria"].get("ambiente", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf,
                                 f'TIPO EMISIÓN: {tipo_emision.get(datos_factura["infoTributaria"].get("tipoEmision", "0"), "DESCONOCIDO")}',
                                 y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= dividir_y_centrar_texto(pdf, 'CLAVE DE ACCESO', y, x, ancho_bloque, "Helvetica", TAM_9)
    y -= ESPACIADO_CONTENIDO_RIDE * 2
    # Escribimos el codigo de barras y el numero de autorizacion centrada.
    barcode = code128.Code128(datos_factura["infoTributaria"]["claveAcceso"], barHeight=10 * mm, barWidth=0.2565 * mm)
    gap = barcode.width / mm
    newx = x + (ancho_bloque / 2.0) - (gap / 2)
    barcode.drawOn(pdf, newx * mm, y * mm)
    y -= ESPACIADO_CONTENIDO_RIDE
    y -= dividir_y_centrar_texto(pdf, datos_factura["infoTributaria"]["claveAcceso"], y, x, ancho_bloque,
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


def datos_cliente_fac(pdf, ult_x, ult_y, datos_factura):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE
    alto_bloque = y
    ancho_bloque = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2
    # Seteamos fuente y tamano
    pdf.setFont("Helvetica", TAM_8)
    y -= ESPACIADO_CONTENIDO_RIDE
    # Escribimos la razon social
    pdf.drawString((x + 2) * mm, y * mm,
                   f'RAZÓN SOCIAL/NOMBRES Y APELLIDOS: {datos_factura["infoFactura"]["razonSocialComprador"]}')
    # Escribimos la identificacion
    temp_texto = f'IDENTIFICACIÓN: {datos_factura["infoFactura"]["identificacionComprador"]}'
    tam_texto = pdf.stringWidth(temp_texto, "Helvetica", TAM_8) / mm
    temp_x = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2 - tam_texto
    pdf.drawString(temp_x * mm, y * mm, temp_texto)
    y -= ESPACIADO_CONTENIDO_RIDE

    # Escribimos fecha emision
    pdf.drawString((x + 2) * mm, y * mm, f'IDENTIFICACIÓN: {datos_factura["infoFactura"]["fechaEmision"]}')
    # Escribimos la guia remision
    temp_texto = f'GUIA REMISIÓN: {datos_factura["infoFactura"].get("guiaRemision", "N/A")}'
    tam_texto = pdf.stringWidth(temp_texto, "Helvetica", TAM_8) / mm
    temp_x = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2 - tam_texto
    pdf.drawString(temp_x * mm, y * mm, temp_texto)
    y -= ESPACIADO_CONTENIDO_RIDE / 2

    # alto del bloque el inicial y menos el actual
    alto_bloque -= y

    # Dibujamos un Cuadrado a partir de un rectángulo redondeado
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)

    return 0, y


def calcular_lineas_texto(texto, caracteres_por_linea):
    # Calcula el número total de líneas que se necesitan para un texto, dado un número fijo de caracteres por línea.
    # Usa math.ceil para redondear hacia arriba y asegurarse de que cualquier texto que exceda un múltiplo completo
    # de caracteres_por_linea se cuente como una línea adicional.
    return math.ceil(len(texto) / caracteres_por_linea)


def procesar_detalles(pdf, ult_x, ult_y, detalles):
    # Calcula el máximo tamaño que puede tener la tabla de detalles en la página actual,
    # teniendo en cuenta el espacio superior reservado (ESPACIADO_BLOQUES_RIDE).
    max_pos_tam_tabla = ult_y - ESPACIADO_BLOQUES_RIDE * 2

    # Altura en mm por línea. Esta variable define la altura de una línea de texto en la tabla.
    tamanio_linea = 6

    # Altura inicial acumulada incluye las dos líneas del encabezado de la tabla.
    altura_acumulada = 2 * tamanio_linea

    # Lista para acumular los detalles que se pueden procesar dentro del límite de altura de la página actual.
    detalles_procesados = []

    # Itera sobre cada detalle en la lista de detalles proporcionada.
    for detalle in detalles:
        # Construye la descripción concatenando la descripción del producto con la marca, si esta última está disponible.
        descripcion = detalle['descripcion'] + (' -**- ' + detalle.get('marcaProducto', '') if detalle.get('marcaProducto') else '')

        # Calcula el número de líneas necesarias para la descripción, asumiendo 31 caracteres por línea.
        lineas_descripcion = calcular_lineas_texto(descripcion, 31)

        # Calcula el número de líneas para el código principal y auxiliar, asumiendo 14 caracteres por línea.
        lineas_codigo_principal = calcular_lineas_texto(detalle.get('codigoPrincipal', ''), 14)
        lineas_codigo_auxiliar = calcular_lineas_texto(detalle.get('codigoAuxiliar', ''), 14)

        # Determina el número máximo de líneas requerido entre descripción y códigos.
        max_lineas = max(lineas_descripcion, lineas_codigo_principal, lineas_codigo_auxiliar)

        # Calcula la altura total que ocupará este detalle en la tabla, basado en el número máximo de líneas.
        altura_detalle = max_lineas * tamanio_linea

        # Verifica si agregar este detalle excedería el espacio disponible en la página.
        if altura_acumulada + altura_detalle > max_pos_tam_tabla:
            # Si hay detalles acumulados hasta ahora, los procesa antes de continuar.
            if detalles_procesados:
                # Dibuja los detalles acumulados en la tabla y calcula la nueva posición de 'ult_y'.
                ult_y = contenido_fac(pdf, ult_x, ult_y, detalles_procesados)
                # Crea una nueva página en el PDF.
                pdf.showPage()
                # Establece el límite de tamaño para la tabla en la nueva página.
                max_pos_tam_tabla = ALTO_A4 - ESPACIADO_BLOQUES_RIDE * 2
                # Restablece 'ult_y' para la nueva página, teniendo en cuenta el espacio superior.
                ult_y = ALTO_A4 - ESPACIADO_BLOQUES_RIDE
                # Limpia la lista de detalles procesados para empezar de nuevo.
                detalles_procesados = []
                # Restablece la altura acumulada para la nueva página, incluyendo el encabezado.
                altura_acumulada = 2 * tamanio_linea
            else:
                # Si no hay detalles procesados y el detalle actual no cabe, fuerza a una nueva página.
                pdf.showPage()
                # Procesa el detalle actual directamente en la nueva página.
                ult_y = contenido_fac(pdf, ult_x, ALTO_A4 - ESPACIADO_BLOQUES_RIDE, [detalle])
                # Restablece la altura acumulada para continuar con los siguientes detalles.
                altura_acumulada = 2 * tamanio_linea
                continue  # Continúa con el próximo detalle.

        # Acumula la altura de este detalle y lo añade a la lista de detalles procesados.
        altura_acumulada += altura_detalle
        detalles_procesados.append(detalle)

    # Después de procesar todos los detalles, si quedan detalles por procesar, los dibuja.
    if detalles_procesados:
        ult_y = contenido_fac(pdf, ult_x, ult_y, detalles_procesados)

    # Devuelve la última posición 'y' después de procesar los detalles, para continuar dibujando desde ahí.
    return ult_y


def contenido_fac(pdf, ult_x, ult_y, detalles):
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE

    ancho_bloque = ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2
    p8_center = ParagraphStyle('parrafos', fontSize=8, fontName="Helvetica", alignment=TA_CENTER)
    p8_right = ParagraphStyle('parrafos', fontSize=8, fontName="Helvetica", alignment=TA_RIGHT)
    data = []
    data.append([Paragraph('Cod. Principal', p8_center),
                 Paragraph('Cod. Auxiliar', p8_center),
                 Paragraph('CR', p8_center),
                 Paragraph('Descripción', p8_center),
                 Paragraph('#', p8_center),
                 Paragraph('Precio Uni.', p8_center),
                 Paragraph('Desc.', p8_center),
                 Paragraph('Precio Tot.', p8_center)])

    for detalle in detalles:
        # Extracción de los campos requeridos del detalle
        codigo_principal = detalle.get('codigoPrincipal', '')
        codigo_auxiliar = detalle.get('codigoAuxiliar', '')  # Usa get para manejar la ausencia del campo
        descripcion = detalle['descripcion'] + (' -**- ' + detalle.get('marcaProducto', '') if detalle.get('marcaProducto') else '')

        # Formatear los valores numéricos
        cantidad = int(float(detalle['cantidad']))  # Convertir a entero
        precio_unitario = '{:.3f}'.format(float(detalle['precioUnitario']))
        descuento = '{:.3f}'.format(float(detalle.get('descuento', '0.00')))
        precio_total_sin_impuesto = '{:.3f}'.format(float(detalle['precioTotalSinImpuesto']))
        # Agregar los valores formateados a la lista 'data'
        data.append([
            Paragraph(codigo_principal, p8_center),
            Paragraph(codigo_auxiliar, p8_center),
            Paragraph('', p8_center),
            Paragraph(descripcion, p8_center),
            Paragraph(str(cantidad), p8_center),  # Convertir cantidad a cadena
            Paragraph(precio_unitario, p8_right),
            Paragraph(descuento, p8_right),
            Paragraph(precio_total_sin_impuesto, p8_right)
        ])
    col_width = (ancho_bloque / float(24))
    tabla_contenido = Table(data,
                            colWidths=[col_width * 3 * mm, col_width * 3 * mm, col_width * 2 * mm, col_width * 8 * mm,
                                       col_width * 2 * mm,
                                       col_width * 2 * mm, col_width * 2 * mm, col_width * 2 * mm])
    tabla_contenido.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    tabla_contenido.wrapOn(pdf, 500, 500)
    w, h = tabla_contenido.wrap(0, 0)
    alto_tabla = h / mm
    tabla_contenido.drawOn(pdf, x * mm, (y - alto_tabla) * mm)
    y -= alto_tabla
    return y


def procesar_info_adicional(pdf, ult_x, ult_y, detalles):
    max_pos_tam_bloque = ult_y - ESPACIADO_BLOQUES_RIDE * 2
    # Altura en mm por línea. Esta variable define la altura de una línea de texto en la tabla.
    tamanio_linea = 6
    altura_acumulada = 0
    # Lista para acumular los detalles que se pueden procesar dentro del límite de altura de la página actual.
    detalles_procesados = []

    # Calcular altura total necesaria y recopilar detalles
    for detalle in detalles:
        for clave, valor in detalle.items():
            texto = f'{clave}:  {valor}'
            # Aquí se puede mejorar calculando el número real de líneas que ocuparía el texto
            altura_acumulada += tamanio_linea
            detalles_procesados.append(detalle)  # Añadir detalle para procesamiento

    # Verificar si la altura total excede el espacio disponible en la página actual
    if altura_acumulada > max_pos_tam_bloque:
        pdf.showPage()  # Crear una nueva página
        y = ALTO_A4 - ESPACIADO_BLOQUES_RIDE * 2
        # Dibujar los detalles procesados en la página actual o nueva
        inf_adicional_fac(pdf, ult_x, y, detalles_procesados)

    else:
        # Dibujar los detalles procesados en la página actual o nueva
        inf_adicional_fac(pdf, ult_x, ult_y, detalles_procesados)


def inf_adicional_fac(pdf, ult_x, ult_y, datos):
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

    contador_items = 0  # Contador para los ítems
    for item in datos:
        for clave, valor in item.items():
            texto = f'{clave}:  {valor}'
            texto_cortado = texto[:75]  # Limitar la longitud del texto a 75 caracteres
            pdf.drawString((x + 2) * mm, y * mm, texto_cortado)
            y -= ESPACIADO_CONTENIDO_RIDE  # Ajustar y para la siguiente línea
        contador_items += 1  # Incrementar el contador de ítems

    alto_bloque -= y
    pdf.roundRect(x * mm, y * mm, ancho_bloque * mm, alto_bloque * mm, 5, stroke=1, fill=0)
    return y, alto_bloque + y


def totales_fac(pdf, ult_x, ult_y, datos):
    max_pos_tam_tabla = ult_y - ESPACIADO_BLOQUES_RIDE * 2
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y

    ancho_bloque_ant = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2) / 1.5
    # ESTO NO LO VES NI EN LA NASA
    tam_col_izq = pdf.stringWidth('Subtotal no Objeto de IVA            ', "Helvetica", 8) / mm
    tam_col_der = ANCHO_A4 - ancho_bloque_ant - tam_col_izq - ESPACIADO_BLOQUES_RIDE * 3

    p8 = ParagraphStyle('parrafos', fontSize=TAM_8, fontName="Helvetica")
    p8_right = ParagraphStyle('parrafos', fontSize=TAM_8, fontName="Helvetica", alignment=TA_RIGHT)

    # Crear un diccionario filtrado con solo los valores diferentes de 0
    datos_filtrados = {k: v for k, v in datos.items() if v != 0.0}

    # Convertir valores numéricos a cadenas de texto
    data = []
    for key, value in datos_filtrados.items():
        data.append([Paragraph(key.replace('_', ' ').upper(), p8), Paragraph('{:.2f}'.format(value), p8_right)])

    tabla_totales = Table(data, colWidths=(tam_col_izq * mm, tam_col_der * mm))
    tabla_totales.setStyle(TableStyle([('ALIGN', (1, 0), (0, 0), 'LEFT'),
                                       ('ALIGN', (-1, 0), (0, -1), 'RIGHT'),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                       ]))
    # Dibujar la tabla en el PDF
    tabla_totales.wrapOn(pdf, 500, 500)
    w, h = tabla_totales.wrap(0, 0)
    alto_tabla = h / mm
    if alto_tabla > max_pos_tam_tabla:
        pdf.showPage()
        y = ALTO_A4 - ESPACIADO_BLOQUES_RIDE * 2
        tabla_totales.drawOn(pdf, (x + ancho_bloque_ant + ESPACIADO_BLOQUES_RIDE) * mm, y * mm - h)
    else:
        tabla_totales.drawOn(pdf, (x + ancho_bloque_ant + ESPACIADO_BLOQUES_RIDE) * mm, y * mm - h)
    y -= alto_tabla
    return y


def calcular_totales_fac(datos_factura):
    subtotal_0 = subtotal_12 = subtotal_15 = subtotal_5 = subtotal_14 = subtotal_no_sujeto = subtotal_exento = ice = iva_12 = iva_14 = iva_5 = iva_15 = irbpnr = 0.0

    for impuesto in datos_factura['infoFactura']['totalConImpuestos']:
        base_imponible = float(impuesto['baseImponible'])
        valor = float(impuesto['valor'])
        codigo_porcentaje = impuesto['codigoPorcentaje']

        if impuesto['codigo'] == '2':  # IVA
            if codigo_porcentaje == '0':
                subtotal_0 += base_imponible
            elif codigo_porcentaje == '2':
                subtotal_12 += base_imponible
                iva_12 += valor
            elif codigo_porcentaje == '3':
                subtotal_14 += base_imponible
                iva_14 += valor
            elif codigo_porcentaje == '4':
                subtotal_15 += base_imponible
                iva_15 += valor
            elif codigo_porcentaje == '5':
                subtotal_5 += base_imponible
                iva_5 += valor
            elif codigo_porcentaje == '6':
                subtotal_no_sujeto += base_imponible
            elif codigo_porcentaje == '7':
                subtotal_exento += base_imponible

        elif impuesto['codigo'] == '3':  # ICE
            ice += valor

        elif impuesto['codigo'] == '5':  # IRBPNR
            irbpnr += valor

    subtotal_sin_impuestos = float(datos_factura['infoFactura']['totalSinImpuestos'])
    descuento = float(datos_factura['infoFactura'].get('totalDescuento', 0))
    propina = float(datos_factura['infoFactura'].get('propina', 0))
    importe_total = float(datos_factura['infoFactura'].get('importeTotal', 0))
    # Si importe total no está presente o es 0.00, calcularlo
    if importe_total == 0.00:
        importe_total = subtotal_sin_impuestos + iva_5 + iva_15 + irbpnr + ice + propina - descuento

    return {
        'SUBTOTAL SIN IMPUESTOS': subtotal_sin_impuestos,
        'SUBTOTAL 0%': subtotal_0,
        'SUBTOTAL 5%': subtotal_5,
        'SUBTOTAL 12%': subtotal_12,
        'SUBTOTAL 14%': subtotal_14,
        'SUBTOTAL 15%': subtotal_15,
        'Subtotal No Objeto de IVA': subtotal_no_sujeto,
        'Subtotal Exento de IVA': subtotal_exento,
        'DESCUENTO': descuento,
        'ICE': ice,
        'IRBPNR': irbpnr,
        'IVA 5%': iva_5,
        'IVA 12%': iva_12,
        'IVA 14%': iva_14,
        'IVA 15%': iva_15,
        'PROPINA': propina,
        'TOTAL': importe_total
    }


def tabla_formas_pago_fac(pdf, ult_x, ult_y, formas_pago):
    max_pos_tam_tabla = ult_y - ESPACIADO_BLOQUES_RIDE * 2
    x = ult_x + ESPACIADO_BLOQUES_RIDE
    # Nos separamos del borde superior
    y = ult_y - ESPACIADO_BLOQUES_RIDE
    ancho_bloque = float(ANCHO_A4 - ESPACIADO_BLOQUES_RIDE * 2) / 1.5
    tam_col_izq = ancho_bloque / 3
    tam_col_der = ancho_bloque / 1.5
    data = [["Forma de Pago", "Monto"]]
    for pago in formas_pago:
        data.append(pago.split(": ", 1))  # Divide la cadena en forma de pago y monto
    # Crear la tabla
    tabla = Table(data, colWidths=[tam_col_izq * mm, tam_col_der * mm])
    tabla.setStyle(TableStyle([('ALIGN', (1, 0), (0, 0), 'LEFT'),
                               ('ALIGN', (-1, 0), (0, -1), 'RIGHT'),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black), ]))
    # Dibujar la tabla en el PDF
    tabla.wrapOn(pdf, 500, 500)
    w, h = tabla.wrap(0, 0)
    alto_tabla = h / mm
    if alto_tabla > max_pos_tam_tabla:
        pdf.showPage()
        y = temp_y = ALTO_A4 - ESPACIADO_BLOQUES_RIDE * 2
        tabla.drawOn(pdf, x * mm, (y - alto_tabla) * mm)
    else:
        tabla.drawOn(pdf, x * mm, (y - alto_tabla) * mm)
        temp_y = y
    y -= alto_tabla
    return ancho_bloque, y, temp_y


def obtener_formas_pago_fac(datos_factura):
    formas_pago = []
    # Verificar si 'pagos' existe y no está vacío en datos_factura
    pagos = datos_factura.get('infoFactura', {}).get('pagos', [])
    if pagos:
        for pago in pagos:
            forma_pago_nombre = nombres_formapago.get(pago['formaPago'], 'Desconocido')
            formas_pago.append(f'{forma_pago_nombre}: {pago["total"]}')
    formas_pago.append(f'# FACTURA: ')
    formas_pago.append(f'# RETENCIÓN: ')
    formas_pago.append(f'FORMA PAGO/#: ')
    formas_pago.append(f'REVISADO/FECHA: ')
    formas_pago.append(f'ETIQUETADO/FECHA: ')
    return formas_pago


# Funcion que retorna el archivo con el pdf de la factura para enviar por correo.
def imprimir_factura_pdf(documento, ruta_archivo, ruta_logo):
    # Creo el canvas y le paso el buffer.
    p = canvas.Canvas(ruta_archivo, pagesize=A4)
    # Ubico el inicio de las cordenadas en la esquina superior izquierda
    # Empiezo a agregar las partes modularmente de izquierda a derecha de arriba abajo.
    # El ult_y lo coloco directamente como ALTO_A4, ya que inicio desde la parte de arriba.
    ult_x, ult_y = datos_emisor_fac(p, 0, ALTO_A4, documento, ruta_logo)
    detalle_fac(p, ult_x, ALTO_A4, documento)
    ult_x, ult_y = datos_cliente_fac(p, 0, ult_y, documento)
    ult_y = procesar_detalles(p, ult_x, ult_y, documento['detalles'])
    datos_forma_pago = obtener_formas_pago_fac(documento)
    ult_x, ult_y, temp_y = tabla_formas_pago_fac(p, 0, ult_y, datos_forma_pago)
    totales_fac(p, 0, temp_y, calcular_totales_fac(documento))
    procesar_info_adicional(p, 0, ult_y, documento['infoAdicional'])
    p.save()
