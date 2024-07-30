from librerias.diccionarios import nombre_impuesto_retencion


# Función para analizar y extraer información del contenido de una factura
# Recibe un elemento etree y devuelve un diccionario con el contenido de la factura.
def comprobante_a_dic_factura(comprobante_tree):
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoFactura": {},
        "detalles": [],
        "infoAdicional": [],
    }

    # Extraer elementos de infoTributaria
    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    # Extraer elementos de infoFactura
    info_factura = root.find("infoFactura")
    for element in info_factura:
        data["infoFactura"][element.tag] = element.text

    # Extraer y anidar totalConImpuestos
    total_con_impuestos = info_factura.find("totalConImpuestos")
    if total_con_impuestos is not None:
        data["infoFactura"]["totalConImpuestos"] = []
        for impuesto in total_con_impuestos:
            impuesto_data = {element.tag: element.text for element in impuesto}
            data["infoFactura"]["totalConImpuestos"].append(impuesto_data)

    # Extraer y anidar pagos
    pagos = info_factura.find("pagos")
    if pagos is not None:
        data["infoFactura"]["pagos"] = []
        for pago in pagos:
            pago_data = {element.tag: element.text for element in pago}
            data["infoFactura"]["pagos"].append(pago_data)

    # Extraer y anidar detalles
    detalles = root.find("detalles")
    for detalle in detalles:
        detalle_data = {element.tag: element.text for element in detalle}
        # Extraer y anidar impuestos de cada detalle
        impuestos = detalle.find("impuestos")
        if impuestos is not None:
            detalle_data["impuestos"] = []
            for impuesto in impuestos:
                impuesto_data = {element.tag: element.text for element in impuesto}
                detalle_data["impuestos"].append(impuesto_data)
            data["detalles"].append(detalle_data)

    # Extraer y anidar infoAdicional
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            info_adicional_data = {campo_adicional.get("nombre"): campo_adicional.text}
            data["infoAdicional"].append(info_adicional_data)

    return data


def comprobante_a_dic_retencion(comprobante_tree):
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoCompRetencion": {},
        "impuestos": [],
        "maquinaFiscal": {},
        "infoAdicional": []
    }

    # Extraer elementos de infoTributaria
    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    # Extraer elementos de infoCompRetencion
    info_comp_retencion = root.find("infoCompRetencion")
    for element in info_comp_retencion:
        data["infoCompRetencion"][element.tag] = element.text

    impuestos = root.find("impuestos")
    if impuestos is not None and len(impuestos) > 0:
        for impuesto in impuestos:
            impuesto_data = {}
            for element in impuesto:
                impuesto_data[element.tag] = element.text
            tipo_impuesto = nombre_impuesto_retencion.get(impuesto_data.get('codigo'), 'Otro')
            impuesto_data['tipoImpuesto'] = tipo_impuesto
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

    # Extraer elementos de maquinaFiscal
    maquina_fiscal = root.find("maquinaFiscal")
    if maquina_fiscal is not None:
        for element in maquina_fiscal:
            data["maquinaFiscal"][element.tag] = element.text

    # Extraer elementos de infoAdicional (si existen)
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            data["infoAdicional"].append({
                "nombre": campo_adicional.get("nombre"),
                "valor": campo_adicional.text
            })

    return data


def comprobante_a_dic_nota_credito(comprobante_tree):
    root = comprobante_tree

    data = {
        "infoTributaria": {},
        "infoNotaCredito": {},
        "detalles": [],
        "infoAdicional": []
    }

    info_tributaria = root.find("infoTributaria")
    for element in info_tributaria:
        data["infoTributaria"][element.tag] = element.text

    info_nota_credito = root.find("infoNotaCredito")
    for element in info_nota_credito:
        if element.tag == "compensaciones":
            compensaciones = []
            for compensacion in element:
                comp_data = {}
                for comp_element in compensacion:
                    comp_data[comp_element.tag] = comp_element.text
                compensaciones.append(comp_data)
            data["infoNotaCredito"][element.tag] = compensaciones
        elif element.tag == "totalConImpuestos":
            total_impuestos = []
            for total_impuesto in element:
                total_impuesto_data = {}
                for imp_element in total_impuesto:
                    total_impuesto_data[imp_element.tag] = imp_element.text
                total_impuestos.append(total_impuesto_data)
            data["infoNotaCredito"][element.tag] = total_impuestos
        else:
            data["infoNotaCredito"][element.tag] = element.text

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

    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional:
            data["infoAdicional"].append({
                "nombre": campo_adicional.get("nombre"),
                "valor": campo_adicional.text
            })

    return data