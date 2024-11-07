import logging
import os
import shutil
from tkinter import filedialog
from sri_xml_bot.librerias.utils import encontrar_y_eliminar_duplicados
from sri_xml_bot.librerias.utils_xml import procesar_archivo_xml, extraer_tipo, extraer_ruc_receptor, \
    extraer_ruc_emisor, extraer_clave_autorizacion, extraer_secuencial, extraer_fecha


def ordenar_documentos(estructura_nombre, estructura_ruta, ruc_actual, tipo_documento):
    """
    Lógica para ordenar documentos en una carpeta especificada por el usuario.

    Args:
        estructura_nombre (str): Formato de nombre del archivo XML.
        estructura_ruta (str): Ruta de guardado personalizada.
        ruc_actual (str): RUC actual seleccionado.
    """
    try:
        # Aquí iría el código para descargar los documentos.
        logging.debug("Iniciando descarga de documentos.")
        directorio = filedialog.askdirectory(title="Seleccione la carpeta de documentos a ordenar")
        if directorio:
            try:
                archivos_eliminados = encontrar_y_eliminar_duplicados(directorio)
                archivos_organizados = organizar_archivos_xml(directorio, estructura_ruta, estructura_nombre, ruc_actual, tipo_documento)
            except Exception as e:
                logging.exception(f"Error al ordenar documentos en el directorio {directorio}: {e}")
        else:
            logging.info("No se seleccionó ningún directorio para ordenar los documentos.")


        logging.debug("Descarga de documentos completada.")
    except Exception as e:
        logging.exception("Error durante la descarga de documentos.")
        raise e


def organizar_archivos_xml(directorio, estructura_ruta, estructura_nombre, ruc_procesado, RecEmi):
    """
    Organiza archivos XML en el directorio especificado según la estructura dada.

    Args:
        directorio (str): Directorio donde se encuentran los archivos XML.
        estructura_ruta (list): Lista que define la estructura de carpetas.
        estructura_nombre (str): Formato del nombre del archivo XML.
        ruc_procesado (str): RUC para filtrar los documentos.
        RecEmi (str): ('recibidos' o 'emitidos').

    Returns:
        list: Lista de mensajes informando del resultado del proceso.
    """
    mensajes = []

    for archivo in os.listdir(directorio):
        if archivo.endswith('.xml'):
            ruta_archivo = os.path.join(directorio, archivo)
            documento = procesar_archivo_xml(ruta_archivo)

            if documento is not None:
                # Extraer la información clave del documento
                tipo_documento = extraer_tipo(documento)
                ruc_receptor = extraer_ruc_receptor(documento, tipo_documento)
                ruc_emisor = extraer_ruc_emisor(documento)
                clave_acceso = extraer_clave_autorizacion(documento)
                secuencial = extraer_secuencial(documento)
                anio, mes, _ = extraer_fecha(documento, tipo_documento)

                # Determinar el RUC que corresponde al tipo de documento
                if RecEmi == 'recibidos' and ruc_procesado == ruc_receptor:
                    ruc_valido = ruc_receptor
                elif RecEmi == 'emitidos' and ruc_procesado == ruc_emisor:
                    ruc_valido = ruc_emisor
                else:
                    # Si el RUC no coincide con el tipo de documento, continuar con el siguiente archivo
                    continue

                # Construir la ruta de guardado en base a la estructura proporcionada
                ruta_guardado = directorio
                for parte in estructura_ruta:
                    if parte == "Año":
                        ruta_guardado = os.path.join(ruta_guardado, anio)
                    elif parte == "Mes":
                        ruta_guardado = os.path.join(ruta_guardado, mes)
                    elif parte == "RUC":
                        ruta_guardado = os.path.join(ruta_guardado, ruc_valido)
                    elif parte == "RecEmi":
                        ruta_guardado = os.path.join(ruta_guardado, RecEmi)
                    elif parte == "TipoDocumento":
                        ruta_guardado = os.path.join(ruta_guardado, tipo_documento)
                    elif parte == "XML":
                        ruta_guardado = os.path.join(ruta_guardado, "xml")

                # Crear la estructura de carpetas si no existe
                os.makedirs(ruta_guardado, exist_ok=True)

                # Crear el nombre del archivo según la estructura especificada
                if estructura_nombre == 'clave_acceso':
                    nombre_archivo = clave_acceso + '.xml'
                elif estructura_nombre == 'ruc_secuencial':
                    nombre_archivo = (ruc_emisor if RecEmi == 'recibidos' else ruc_receptor) + '_' + secuencial + '.xml'
                elif estructura_nombre == 'secuencial':
                    nombre_archivo = secuencial + '.xml'
                else:
                    nombre_archivo = clave_acceso + '.xml'  # Por defecto, usar clave de acceso

                # Mover el archivo al destino final
                destino_archivo = os.path.join(ruta_guardado, nombre_archivo)
                shutil.move(ruta_archivo, destino_archivo)
                mensajes.append(f"Archivo '{archivo}' movido a '{destino_archivo}'.")

            else:
                # Si el archivo XML no pudo ser procesado
                mensajes.append(f"Error al procesar el archivo {archivo}. Información insuficiente.")

    mensajes.append("Todos los archivos leídos correctamente han sido organizados.")
    return mensajes
