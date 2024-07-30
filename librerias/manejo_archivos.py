import re
import xml.etree.ElementTree as ET
from librerias.diccionarios import nombres_comprobantes
from funciones_auxiliares import comprobante_a_dic_factura, comprobante_a_dic_retencion, comprobante_a_dic_nota_credito


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
            datos_extras['fechaAutorizacion'] = autorizacion.findtext('fechaAutorizacion')
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
                # Reemplaza las llamadas a funciones específicas de procesamiento de comprobantes según el tipo
                # Aquí deberías llamar a la función apropiada como comprobante_a_dic_factura(comprobante_tree) según el tipo_documento
                # Por ejemplo:
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
