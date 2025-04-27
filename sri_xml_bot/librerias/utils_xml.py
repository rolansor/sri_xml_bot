import re
import xml.etree.ElementTree as ET
import datetime
from sri_xml_bot.librerias.diccionarios import nombres_comprobantes, nombre_impuesto_retencion


# ================================
# Funciones de Extracción de Datos
# ================================

def extraer_tipo(documento):
    """
    Extrae el tipo de documento a partir de la información adicional.

    Args:
        documento (dict): Diccionario que contiene los datos del documento.

    Returns:
        str: Tipo de documento.
    """
    return documento['datos_extras']['tipoDocumento']


def extraer_ruc_receptor(documento, tipo):
    """
    Extrae el RUC del receptor dependiendo del tipo de documento.

    Args:
        documento (dict): Diccionario que contiene los datos del documento.
        tipo (str): Tipo del documento.

    Returns:
        str: RUC del receptor, con "001" agregado si tiene 10 dígitos.
    """
    campo_ruc = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    #TODO: Validar que el identificador del ruc receptor segun el tipo de documento electronico.
    ruc = documento[campo_ruc[tipo]]['identificacionComprador' if tipo != 'comprobantes_de_retencion' else 'identificacionSujetoRetenido']
    return ruc + "001" if len(ruc) == 10 else ruc


def extraer_ruc_emisor(documento):
    """
    Extrae el RUC del emisor del documento.

    Args:
        documento (dict): Diccionario que contiene los datos del documento.

    Returns:
        str: RUC del emisor.
    """
    return documento['infoTributaria']['ruc']


def extraer_secuencial(documento):
    """
    Extrae el secuencial completo del documento (estab, ptoEmi, secuencial).

    Args:
        documento (dict): Diccionario que contiene los datos del documento.

    Returns:
        str: Secuencial completo en formato "estab-ptoEmi-secuencial".
    """
    return documento['infoTributaria']['estab'] + '-' + documento['infoTributaria']['ptoEmi'] + '-' + documento['infoTributaria']['secuencial']


def extraer_clave_autorizacion(documento):
    """
    Extrae la clave de autorización del documento.

    Args:
        documento (dict): Diccionario que contiene los datos del documento.

    Returns:
        str: Clave de acceso.
    """
    return documento['infoTributaria']['claveAcceso']


def extraer_fecha(documento, tipo):
    """
    Extrae la fecha de emisión del documento en formato año, mes y día.

    Args:
        documento (dict): Diccionario que contiene los datos del documento.
        tipo (str): Tipo del documento.

    Returns:
        tuple: Año, mes y día como strings.
    """
    campo_fecha = {
        'facturas': 'infoFactura',
        'comprobantes_de_retencion': 'infoCompRetencion',
        'notas_de_credito': 'infoNotaCredito'
    }
    fecha_emision_str = documento[campo_fecha[tipo]]['fechaEmision']
    fecha_emision = datetime.datetime.strptime(fecha_emision_str, "%d/%m/%Y")
    return str(fecha_emision.year), str(fecha_emision.month).zfill(2), str(fecha_emision.day).zfill(2)


# ============================
# Procesamiento del Archivo XML
# ============================

def procesar_archivo_xml(file_path):
    """
    Procesa un archivo XML y extrae la estructura del documento.

    Args:
        file_path (str): Ruta del archivo XML.

    Returns:
        dict or None: Diccionario con la información del documento o None si falla.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    datos_extras = {}

    # Determina si el XML contiene 'autorizacion' para mayor claridad
    autorizacion = None
    if root.tag == 'autorizaciones':
        autorizaciones = root.findall('autorizacion')
        autorizacion = autorizaciones[-1] if autorizaciones else None
    elif root.find('.//autorizacion') is not None:
        autorizacion = root.find('.//autorizacion')
    else:
        autorizacion = root  # Si no hay 'autorizacion', se usa el root

    # Extrae detalles generales como estado, fecha de autorización y ambiente
    if autorizacion is not None:
        if autorizacion.tag != 'autorizaciones':
            datos_extras['estado'] = autorizacion.findtext('estado') or 'desconocido'
            datos_extras['fechaAutorizacion'] = autorizacion.findtext('fechaAutorizacion') or 'desconocido'
            datos_extras['ambiente'] = autorizacion.findtext('ambiente') or 'desconocido'

        # Procesar el contenido de 'comprobante' como string o como ET
        comprobante_str = autorizacion.findtext('.//comprobante') or ET.tostring(autorizacion, encoding='unicode')
        comprobante_str = re.sub(r'^<\?xml[^>]+\?>', '', comprobante_str.strip())
        comprobante_tree = ET.fromstring(comprobante_str) if '<' in comprobante_str else autorizacion

        # Extraer el tipo de documento y mapearlo a nombres legibles
        tipo_doc_element = comprobante_tree.find('.//infoTributaria/codDoc')
        if tipo_doc_element is not None:
            tipo_doc = tipo_doc_element.text
            tipo_documento = nombres_comprobantes.get(tipo_doc, None)
            datos_extras['tipoDocumento'] = tipo_documento

            # Procesar el documento en base a su tipo
            if tipo_documento:
                diccionario_documento = None
                if tipo_documento == 'facturas':
                    diccionario_documento = comprobante_a_dic_factura(comprobante_tree)
                elif tipo_documento == 'comprobantes_de_retencion':
                    diccionario_documento = comprobante_a_dic_retencion(comprobante_tree)
                elif tipo_documento == 'notas_de_credito':
                    diccionario_documento = comprobante_a_dic_nota_credito(comprobante_tree)

                if diccionario_documento is not None:
                    diccionario_documento['datos_extras'] = datos_extras
                    return diccionario_documento
    return None


# ====================================
# Funciones de Conversión de Comprobantes
# ====================================


def comprobante_a_dic_factura(comprobante_tree):
    """
    Convierte un elemento XML de factura en un diccionario.

    Args:
        comprobante_tree (Element): Elemento XML de la factura.

    Returns:
        dict: Diccionario con datos de la factura.
    """
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoFactura": {},
        "detalles": [],
        "infoAdicional": [],
    }

    # Extrae la información de infoTributaria
    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    # Extrae la información de infoFactura y anida totalConImpuestos y pagos
    info_factura = root.find("infoFactura")
    for element in info_factura:
        data["infoFactura"][element.tag] = element.text

    total_con_impuestos = info_factura.find("totalConImpuestos")
    if total_con_impuestos is not None:
        data["infoFactura"]["totalConImpuestos"] = [
            {element.tag: element.text for element in impuesto}
            for impuesto in total_con_impuestos
        ]

    pagos = info_factura.find("pagos")
    if pagos is not None:
        data["infoFactura"]["pagos"] = [
            {element.tag: element.text for element in pago}
            for pago in pagos
        ]

    # Extrae la información de detalles y anida impuestos
    detalles = root.find("detalles")
    for detalle in detalles:
        detalle_data = {element.tag: element.text for element in detalle}
        impuestos = detalle.find("impuestos")
        if impuestos is not None:
            detalle_data["impuestos"] = [
                {element.tag: element.text for element in impuesto}
                for impuesto in impuestos
            ]
        data["detalles"].append(detalle_data)

    # Extrae la información de infoAdicional
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            data["infoAdicional"].append({
                "nombre": campo_adicional.get("nombre"),
                "valor": campo_adicional.text
            })

    return data


def comprobante_a_dic_retencion(comprobante_tree):
    """
    Convierte un elemento XML de comprobante de retención en un diccionario.

    Args:
        comprobante_tree (Element): Elemento XML del comprobante de retención.

    Returns:
        dict: Diccionario con datos del comprobante de retención.
    """
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoCompRetencion": {},
        "impuestos": [],
        "maquinaFiscal": {},
        "infoAdicional": []
    }

    # Extrae la información de infoTributaria
    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    # Extrae la información de infoCompRetencion y la anida en impuestos
    info_comp_retencion = root.find("infoCompRetencion")
    for element in info_comp_retencion:
        data["infoCompRetencion"][element.tag] = element.text

    impuestos = root.find("impuestos")
    if impuestos is not None:
        for impuesto in impuestos:
            impuesto_data = {element.tag: element.text for element in impuesto}
            impuesto_data['tipoImpuesto'] = nombre_impuesto_retencion.get(impuesto_data.get('codigo'), 'Otro')
            data["impuestos"].append(impuesto_data)
    else:
        # Buscar en docsSustento por retenciones si impuestos no se encuentra
        docs_sustento = root.find("docsSustento")
        if docs_sustento is not None:
            for doc_sustento in docs_sustento:
                # Extraer datos generales de docSustento
                codSustento = doc_sustento.find("codSustento").text
                codDocSustento = doc_sustento.find("codDocSustento").text
                numDocSustento = doc_sustento.find("numDocSustento").text
                fechaEmisionDocSustento = doc_sustento.find("fechaEmisionDocSustento").text
                retenciones = doc_sustento.find("retenciones")
                if retenciones is not None:
                    for retencion in retenciones:
                        retencion_data = {}
                        for element in retencion:
                            retencion_data[element.tag] = element.text
                        tipo_impuesto = nombre_impuesto_retencion.get(retencion_data.get('codigo'), 'Otro')
                        retencion_data['codSustento'] = codSustento
                        retencion_data['codDocSustento'] = codDocSustento
                        retencion_data['numDocSustento'] = numDocSustento
                        retencion_data['fechaEmisionDocSustento'] = fechaEmisionDocSustento
                        retencion_data['tipoImpuesto'] = tipo_impuesto
                        data["impuestos"].append(retencion_data)

    # Extrae información de maquinaFiscal
    maquina_fiscal = root.find("maquinaFiscal")
    if maquina_fiscal is not None:
        for element in maquina_fiscal:
            data["maquinaFiscal"][element.tag] = element.text

    # Extrae la información de infoAdicional
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            data["infoAdicional"].append({
                "nombre": campo_adicional.get("nombre"),
                "valor": campo_adicional.text
            })

    return data


def comprobante_a_dic_nota_credito(comprobante_tree):
    """
    Convierte un elemento XML de nota de crédito en un diccionario.

    Args:
        comprobante_tree (Element): Elemento XML de la nota de crédito.

    Returns:
        dict: Diccionario con datos de la nota de crédito.
    """
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoNotaCredito": {},
        "detalles": [],
        "infoAdicional": []
    }

    # Extrae la información de infoTributaria
    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    # Extrae la información de infoNotaCredito y la anida en compensaciones y totalConImpuestos
    info_nota_credito = root.find("infoNotaCredito")
    for element in info_nota_credito:
        if element.tag == "compensaciones":
            data["infoNotaCredito"]["compensaciones"] = [
                {comp_element.tag: comp_element.text for comp_element in compensacion}
                for compensacion in element
            ]
        elif element.tag == "totalConImpuestos":
            data["infoNotaCredito"]["totalConImpuestos"] = [
                {imp_element.tag: imp_element.text for imp_element in total_impuesto}
                for total_impuesto in element
            ]
        else:
            data["infoNotaCredito"][element.tag] = element.text

    # Extrae la información de detalles y anida impuestos y detalles adicionales
    detalles = root.find("detalles")
    for detalle in detalles:
        detalle_data = {}
        for element in detalle:
            if element.tag == "detallesAdicionales":
                detalles_adicionales = []
                for det_adicional in element:
                    detalles_adicionales.append({
                        "nombre": det_adicional.get("nombre"),
                        "valor": det_adicional.get("valor")
                    })
                detalle_data[element.tag] = detalles_adicionales
            elif element.tag == "impuestos":
                impuestos = []
                for impuesto in element:
                    impuesto_data = {}
                    for imp_element in impuesto:
                        impuesto_data[imp_element.tag] = imp_element.text
                    impuestos.append(impuesto_data)
                detalle_data[element.tag] = impuestos
            else:
                detalle_data[element.tag] = element.text
        data["detalles"].append(detalle_data)

    # Extrae la información de infoAdicional
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            data["infoAdicional"].append({
                "nombre": campo_adicional.get("nombre"),
                "valor": campo_adicional.text
            })

    return data
