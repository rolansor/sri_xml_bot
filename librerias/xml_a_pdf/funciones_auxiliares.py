import re
import datetime
import xml.etree.ElementTree as ET
import unicodedata
from reportlab.lib.units import mm
from librerias.xml_a_pdf.constantes import ESPACIADO_CONTENIDO_RIDE
from librerias.diccionarios import nombres_comprobantes
from librerias.funciones_auxiliares import comprobante_a_dic_factura, comprobante_a_dic_retencion, \
    comprobante_a_dic_nota_credito


def dibujar_reglas(c, width, height, interval=1):
    """
    Dibuja reglas en los bordes izquierdo y abajo de una página, utilizando mm.

    Parámetros:
        c (Canvas): El canvas de ReportLab donde se dibujará.
        width (int): El ancho de la página en mm.
        height (int): La altura de la página en mm.
        interval (int): El intervalo entre las marcas de la regla en mm.
    """
    # Número de marcas en cada eje
    num_marks_x = int(width / interval)
    num_marks_y = int(height / interval)

    # Dibujar regla horizontal en la parte inferior
    for i in range(num_marks_x + 1):
        x = i * interval * mm
        if i % 10 == 0:  # Marca larga cada 10 intervalos
            c.line(x, 0, x, 10 * mm)
            c.drawString(x, 5 * mm, str(i * interval))  # Etiquetar cada 10 marcas
        else:  # Marca corta
            c.line(x, 0, x, 5 * mm)

    # Dibujar regla vertical en el lado izquierdo
    for j in range(num_marks_y + 1):
        y = j * interval * mm
        if j % 10 == 0:  # Marca larga cada 10 intervalos
            c.line(0, y, 10 * mm, y)
            c.drawString(5 * mm, y, str(j * interval))  # Etiquetar cada 10 marcas
        else:  # Marca corta
            c.line(0, y, 5 * mm, y)


def dividir_y_centrar_texto(pdf, texto, y, x, ancho_bloque, fuente, tamano_fuente):
    pdf.setFont(fuente, tamano_fuente)
    # Al parecer StringWidth devuelve medidas en mm y no en puntos, por eso se debe transformar esto.
    # SIEMPRE QUE SE USE STRINGWIDTH; SIEMPRE TARADO!
    ancho_texto = pdf.stringWidth(texto, fuente, tamano_fuente) / mm
    y_mm = y * mm  # Convertir medidas a puntos
    # Verificar si el texto cabe en una línea
    if ancho_texto <= ancho_bloque:
        newx = x + (ancho_bloque / 2.0) - (ancho_texto / 2)
        pdf.drawString(newx * mm, y_mm, texto)
        lineas_creadas = 1
    else:
        # Dividir el texto en dos líneas
        palabras = texto.split()
        linea1 = ""
        linea2 = ""

        for palabra in palabras:
            if pdf.stringWidth(linea1 + palabra + " ", fuente, tamano_fuente) / mm < ancho_bloque:
                linea1 += palabra + " "
            else:
                linea2 += palabra + " "

        # Centrar y dibujar la primera línea
        newx = x + (ancho_bloque / 2.0) - (pdf.stringWidth(linea1, fuente, tamano_fuente) / mm / 2)
        pdf.drawString(newx * mm, y_mm, linea1.strip())

        # Centrar y dibujar la segunda línea
        newx = x + (ancho_bloque / 2.0) - (pdf.stringWidth(linea2, fuente, tamano_fuente) / mm / 2)
        pdf.drawString(newx * mm, y_mm - ESPACIADO_CONTENIDO_RIDE * mm, linea2.strip())

        lineas_creadas = 2
    # Segun las lineas creadas retornamos el espaciado en Y que debemos tener.
    return lineas_creadas * ESPACIADO_CONTENIDO_RIDE


def extraer_fecha(documento, tipo):
    campo_fecha = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    fecha_emision_str = documento[campo_fecha[tipo]]['fechaEmision']
    fecha_emision = datetime.datetime.strptime(fecha_emision_str, "%d/%m/%Y")
    return str(fecha_emision.year), str(fecha_emision.month).zfill(2), str(fecha_emision.day).zfill(2)


def extraer_ruc(documento, tipo):
    campo_ruc = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    ruc = documento[campo_ruc[tipo]]['identificacionComprador' if tipo != 'comprobantes_de_retencion' else 'identificacionSujetoRetenido']
    return ruc + "001" if len(ruc) == 10 else ruc


def normalizar_string(s):
    # Convertir el string a minúsculas
    s = s.lower()
    # Normalizar el string para eliminar tildes manteniendo los espacios
    s = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn' or c == ' '))
    return s


def es_gran_contribuyente(documento):
    # Valores que deseas buscar normalizados
    tipos_esperados = ['gran contribuyente', 'grande contribuyente']
    tipos_esperados = [normalizar_string(tipo) for tipo in tipos_esperados]
    # Verificar en infoAdicional
    if 'infoAdicional' in documento:
        info_adicional = documento['infoAdicional']
        for campo in info_adicional:
            if isinstance(campo, dict):
                for clave, valor in campo.items():
                    # Normalizamos tanto la clave como el valor antes de la comparación
                    clave_normalizada = normalizar_string(clave)
                    valor_normalizado = normalizar_string(valor)
                    for tipo_esperado in tipos_esperados:
                        if tipo_esperado in clave_normalizada or tipo_esperado in valor_normalizado:
                            return True
    return False


def es_agente_retencion(documento):
    # Valor que deseas buscar, normalizado
    tipo_esperado = normalizar_string('agente de retencion')
    # Verificar en infoAdicional
    if 'infoAdicional' in documento:
        info_adicional = documento['infoAdicional']
        for campo in info_adicional:
            if isinstance(campo, dict):
                for clave, valor in campo.items():
                    # Normalizamos tanto la clave como el valor antes de la comparación
                    clave_normalizada = normalizar_string(clave)
                    valor_normalizado = normalizar_string(valor)
                    if tipo_esperado in clave_normalizada or tipo_esperado in valor_normalizado:
                        return True
    return False
