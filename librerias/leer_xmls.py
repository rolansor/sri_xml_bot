import re
import xml.etree.ElementTree as ET
import datetime
from librerias.diccionarios import nombres_comprobantes
from librerias.funciones_auxiliares import comprobante_a_dic_factura, comprobante_a_dic_retencion, comprobante_a_dic_nota_credito


def extraer_tipo(documento):
    tipo_documento = documento['datos_extras']['tipoDocumento']
    return tipo_documento


def extraer_ruc_receptor(documento, tipo):
    campo_ruc = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    ruc = documento[campo_ruc[tipo]]['identificacionComprador' if tipo != 'comprobantes_de_retencion' else 'identificacionSujetoRetenido']
    return ruc + "001" if len(ruc) == 10 else ruc


def extraer_ruc_emisor(documento):
    ruc_emisor = documento['infoTributaria']['ruc']
    return ruc_emisor


def extraer_secuencial(documento):
    secuencial = documento['infoTributaria']['estab'] + '-' + documento['infoTributaria']['ptoEmi'] + '-' + documento['infoTributaria']['secuencial']
    return secuencial


def extraer_clave_autorizacion(documento):
    clave_autorizacion = documento['infoTributaria']['claveAcceso']
    return clave_autorizacion


def extraer_fecha(documento, tipo):
    campo_fecha = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    fecha_emision_str = documento[campo_fecha[tipo]]['fechaEmision']
    fecha_emision = datetime.datetime.strptime(fecha_emision_str, "%d/%m/%Y")
    return str(fecha_emision.year), str(fecha_emision.month).zfill(2), str(fecha_emision.day).zfill(2)


def procesar_archivo_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    datos_extras = {}

    # Intentar encontrar 'autorizacion' como en la primera función
    autorizacion = None
    if root.tag == 'autorizaciones':
        autorizaciones = root.findall('autorizacion')
        autorizacion = autorizaciones[-1] if autorizaciones else None
    elif root.find('.//autorizacion') is not None:
        autorizacion = root.find('.//autorizacion')
    else:
        # Si no hay 'autorizacion', trabajar directamente con el root
        autorizacion = root

    # Procesar 'autorizacion' o 'root' dependiendo del caso
    if autorizacion is not None:
        if autorizacion.tag != 'autorizaciones':
            datos_extras['estado'] = autorizacion.findtext('estado') if autorizacion.findtext(
                'estado') else 'desconocido'
            datos_extras['fechaAutorizacion'] = autorizacion.findtext('fechaAutorizacion') if autorizacion.findtext('fechaAutorizacion') else 'desconocido'
            datos_extras['ambiente'] = autorizacion.findtext('ambiente') if autorizacion.findtext(
                'ambiente') else 'desconocido'

        comprobante_str = autorizacion.findtext('.//comprobante') if autorizacion.find(
            './/comprobante') is not None else ET.tostring(autorizacion, encoding='unicode')
        comprobante_str = re.sub(r'^<\?xml[^>]+\?>', '', comprobante_str.strip())
        comprobante_tree = ET.fromstring(comprobante_str) if '<' in comprobante_str else autorizacion

        tipo_doc_element = comprobante_tree.find('.//infoTributaria/codDoc')
        if tipo_doc_element is not None:
            tipo_doc = tipo_doc_element.text
            tipo_documento = nombres_comprobantes.get(tipo_doc, None)
            datos_extras['tipoDocumento'] = tipo_documento

            if tipo_documento:
                diccionario_documento = None
                if tipo_documento == 'facturas':
                    diccionario_documento = comprobante_a_dic_factura(comprobante_tree)
                elif tipo_documento == 'comprobantes_de_retencion':
                    diccionario_documento = comprobante_a_dic_retencion(comprobante_tree)
                elif tipo_documento == 'notas_de_credito':
                    diccionario_documento = comprobante_a_dic_nota_credito(comprobante_tree)
                # Agregar aquí más condiciones si es necesario

                if diccionario_documento is not None:
                    diccionario_documento['datos_extras'] = datos_extras
                    return diccionario_documento
            else:
                print(f"Tipo de documento desconocido: {tipo_doc}")
        else:
            print("El documento no contiene un tipo de documento reconocido.")
    return None