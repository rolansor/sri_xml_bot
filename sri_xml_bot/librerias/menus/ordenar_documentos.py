import logging
import os
import shutil
from sri_xml_bot.librerias.utils import encontrar_y_eliminar_duplicados
from sri_xml_bot.librerias.utils_xml import procesar_archivo_xml, extraer_tipo, extraer_ruc_receptor, \
    extraer_ruc_emisor, extraer_clave_autorizacion, extraer_secuencial, extraer_fecha


def ordenar_documentos(estructura_nombre, estructura_ruta, ruc_actual, emitido_recibido, directorio, recursivo=False):
    """
    Lógica para ordenar documentos en la carpeta especificada, usando la configuración actual.

    Args:
        estructura_nombre (str): Formato del nombre del archivo (por ejemplo, 'clave_acceso', 'ruc_secuencial', 'secuencial').
        estructura_ruta (str): Cadena que define la estructura de carpetas, separadas por "/".
        ruc_actual (str): RUC actual a procesar.
        emitido_recibido (str): Valor 'recibidos' o 'emitidos' para filtrar los archivos.
        directorio (str): Directorio base en el que se encuentran los archivos XML.
        recursivo (bool): Si es True, se buscarán archivos recursivamente en todos los subdirectorios,
                            es decir para cuidar si se escoge una estructra ya ordenada o en la carpeta de descargas.

    Returns:
        dict: Diccionario con los resultados, por ejemplo:
              { "resultado_organizacion": [...],
                "resultado_eliminados": [...],
                "mensaje_error": [...] }
    """
    mensaje_error = []
    resultado_eliminados = []
    resultado_organizacion = []
    try:
        logging.info("Iniciando ordenación de documentos.")
        # Antes de ordenar se eliminan los duplicados siempre y cuando estemos en la carpeta
        # "maestra", luego se actualiza el mensaje de resultados.
        if not recursivo:
            resultado_eliminados = encontrar_y_eliminar_duplicados(directorio)

        # Ordenar archivos segun la esctructura configurada y agregar mensajes al resultado.
        resultado_organizacion = organizar_archivos_xml(estructura_nombre, estructura_ruta, ruc_actual,
                                                        emitido_recibido, directorio, recursivo)
        logging.info("Ordenación de documentos completada.")

    except Exception as e:
        mensaje_error = [f"Error durante la ordenación de documentos: {e}"]
        logging.error(f"Error durante la ordenación de documentos: {e}")

    return {
        "resultado_organizacion": resultado_organizacion,
        "resultado_eliminados": resultado_eliminados,
        "mensaje_error": mensaje_error
    }


def organizar_archivos_xml(estructura_nombre, estructura_ruta, ruc_procesado, emitido_recibido, directorio, recursivo):
    """
    Organiza archivos XML en el directorio especificado según la estructura dada.

    Args:
        estructura_nombre (str): Formato del nombre del archivo XML.
        estructura_ruta (str): Cadena que define la estructura de carpetas (por ejemplo, "Año/Mes/RUC/RecEmi/XML/TipoDocumento").
        ruc_procesado (str): RUC para filtrar los documentos.
        emitido_recibido (str): 'recibidos' o 'emitidos'.
        directorio (str): Directorio base donde se buscan los archivos XML.
        recursivo (bool): Si es True, buscará de forma recursiva en subdirectorios.

    Returns:
        list: Lista de mensajes informando del resultado del proceso.
    """
    mensajes = []

    # Lista con las partes de la ruta definida en el archivo de
    # configuracion ej: ['Año', 'Mes', 'RUC', 'RecEmi', 'XML', 'TipoDocumento']
    partes_ruta = estructura_ruta.split("/")

    # Lista con los archivos a procesar.
    archivos = []

    # Si es recursivo, vamos a trabajar con documentos ya ordenados, entonces buscamos dentro del directorio actual.
    if recursivo:
        for root, dirs, files in os.walk(directorio):
            for file in files:
                if file.lower().endswith('.xml'):
                    archivos.append(os.path.join(root, file))
    # Si no es recursivo, vamos a trabajar con documentos descargados probablemente, solo obtenemos sus rutas.
    else:
        archivos = [os.path.join(directorio, archivo)
                    for archivo in os.listdir(directorio) if archivo.lower().endswith('.xml')]

    # Contadores para archivos organizados
    contador_organizados = 0
    contador_errores = 0

    # Se procesar por cada archivo individualmente.
    for ruta_archivo in archivos:
        # Se transforma a dict con la funcion procesar_archivo_xml.
        documento = procesar_archivo_xml(ruta_archivo)

        # Si se retorno un dict.
        if documento is not None:
            try:
                tipo_documento = extraer_tipo(documento)
                ruc_receptor = extraer_ruc_receptor(documento, tipo_documento)
                ruc_emisor = extraer_ruc_emisor(documento)
                clave_acceso = extraer_clave_autorizacion(documento)
                secuencial = extraer_secuencial(documento)
                anio, mes, _ = extraer_fecha(documento, tipo_documento)
            except Exception as e:
                mensajes.append(f"Error extrayendo datos de {ruta_archivo}: {e}")
                logging.error(f"Error extrayendo datos de {ruta_archivo}: {e}")
                contador_errores += 1
                continue

            # Determinar el RUC que se esta procesando y que corresponde al tipo de documento.
            if emitido_recibido.lower() == 'recibidos':
                if ruc_procesado != ruc_receptor:
                    continue
                ruc_valido = ruc_receptor
            elif emitido_recibido.lower() == 'emitidos':
                if ruc_procesado != ruc_emisor:
                    continue
                ruc_valido = ruc_emisor
            else:
                mensajes.append(f"Valor incorrecto para emitido_recibido: {emitido_recibido}")
                logging.error(f"Valor incorrecto para emitido_recibido: {emitido_recibido}")
                continue

            # Construir la ruta de guardado en base a la estructura proporcionada
            ruta_guardado = directorio
            for parte in partes_ruta:
                if parte == "Año":
                    ruta_guardado = os.path.join(ruta_guardado, anio)
                elif parte == "Mes":
                    ruta_guardado = os.path.join(ruta_guardado, mes)
                elif parte == "RUC":
                    ruta_guardado = os.path.join(ruta_guardado, ruc_valido)
                elif parte == "RecEmi":
                    ruta_guardado = os.path.join(ruta_guardado, emitido_recibido)
                elif parte == "TipoDocumento":
                    ruta_guardado = os.path.join(ruta_guardado, tipo_documento)
                elif parte == "XML":
                    ruta_guardado = os.path.join(ruta_guardado, "xml")

            # Crear la estructura de carpetas si no existe
            try:
                os.makedirs(ruta_guardado, exist_ok=True)
            except Exception as e:
                mensajes.append(f"Error creando carpeta {ruta_guardado}: {e}")
                logging.error(f"Error creando carpeta {ruta_guardado}: {e}")
                continue

            # Crear el nombre del archivo según la estructura especificada en el archivo de configuracion.
            if estructura_nombre == 'clave_acceso':
                nombre_archivo = clave_acceso + '.xml'
            elif estructura_nombre == 'ruc_secuencial':
                nombre_archivo = (ruc_emisor if emitido_recibido == 'recibidos' else ruc_receptor) + '_' + secuencial + '.xml'
            elif estructura_nombre == 'secuencial':
                nombre_archivo = secuencial + '.xml'
            else:
                nombre_archivo = clave_acceso + '.xml'  # Por defecto, usar clave de acceso

            # Mover el archivo al destino final
            destino_archivo = os.path.join(ruta_guardado, nombre_archivo)
            shutil.move(ruta_archivo, destino_archivo)
            contador_organizados += 1
        else:
            # Si el archivo XML no pudo ser procesado
            contador_errores += 1

    mensajes.append(f"Se han organizado {contador_organizados} archivos correctamente.")
    if contador_errores > 0:
        mensajes.append(f"Hubo {contador_errores} archivos que no se pudieron procesar debido a errores.")

    return mensajes


def desclasificar_xmls(directorio):
    """
    Busca todos los archivos XML en el directorio y en sus subdirectorios
    y los mueve al mismo directorio raíz, dejando una estructura plana.

    Args:
        directorio (str): El directorio seleccionado (fuente y destino).

    Returns:
        dict: Diccionario con:
              - "archivos_movidos": Número total de archivos movidos.
              - "mensajes": Lista de mensajes informando los resultados del proceso.
    """
    mensajes = []  # Lista donde guardaremos mensajes de error o notas del proceso
    contador = 0  # Contador de archivos XML movidos exitosamente

    # Recorremos el directorio y todos sus subdirectorios usando os.walk
    for root, dirs, files in os.walk(directorio):
        # Si estamos en la carpeta raíz, la omitimos (no queremos volver a mover archivos ya en el destino)
        if os.path.abspath(root) == os.path.abspath(directorio):
            continue  # Saltar esta iteración y seguir con la siguiente carpeta

        # Iteramos sobre todos los ficheros en la carpeta actual
        for file in files:
            # Filtramos solo archivos que terminen en .xml (insensible a mayúsculas/minúsculas)
            if file.lower().endswith('.xml'):
                # Construimos la ruta completa de origen
                source_path = os.path.join(root, file)
                # Construimos la ruta destino en la carpeta raíz con el mismo nombre
                dest_path = os.path.join(directorio, file)

                # Si ya existe un archivo con ese nombre en destino, preparamos un sufijo numérico
                base, ext = os.path.splitext(file)  # Separamos nombre base y extensión
                counter = 1  # Inicializamos el contador de sufijo
                # Mientras exista un fichero con la misma ruta destino, incrementamos el sufijo
                while os.path.exists(dest_path):
                    # Generamos un nuevo nombre con _{counter} antes de la extensión
                    dest_path = os.path.join(directorio, f"{base}_{counter}{ext}")
                    counter += 1  # Incrementamos para la siguiente iteración si aún existe

                try:
                    # Intentamos mover el archivo desde source_path a dest_path
                    shutil.move(source_path, dest_path)
                    contador += 1  # Si se mueve correctamente, sumamos uno al contador
                except Exception as e:
                    # En caso de error al mover, registramos y guardamos el mensaje
                    error_msg = f"Error moviendo {source_path}: {e}"
                    mensajes.append(error_msg)  # Añadimos el mensaje a la lista de mensajes
                    logging.error(error_msg)  # Registramos el error en el log

    # Al terminar, devolvemos un dict con el total de archivos movidos y la lista de mensajes
    return {"archivos_movidos": contador, "mensajes": mensajes}