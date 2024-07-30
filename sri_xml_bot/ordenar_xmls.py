import sys
import os
import hashlib
import shutil
from tkinter import filedialog
from librerias.auxiliares import mostrar_mensaje
from librerias.leer_xmls import procesar_archivo_xml, extraer_tipo, extraer_ruc_receptor, extraer_ruc_emisor, \
    extraer_clave_autorizacion, extraer_secuencial, extraer_fecha


def ruta_relativa_recurso(relativa):
    if hasattr(sys, '_MEIPASS'):
        # Si está corriendo dentro de un ejecutable PyInstaller
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)


def cargar_rucs_desde_archivo():
    rucs = {}
    meses_opciones = {"Todos": "00", "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05",
                      "Junio": "06", "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10",
                      "Noviembre": "11", "Diciembre": "12"}

    # Ruta principal
    ruta_archivo = ruta_relativa_recurso('archivos_necesarios/rucs.txt')

    # Verificación de existencia del archivo
    if not os.path.exists(ruta_archivo):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(directorio_actual, '../archivos_necesarios/rucs.txt')

    try:
        with open(ruta_archivo, 'r') as archivo:
            for linea in archivo:
                # Eliminar espacios en blanco y saltos de línea
                linea = linea.strip()
                # Ignorar líneas vacías
                if not linea:
                    continue
                # Dividir la línea en partes separadas por comas
                partes = linea.split(',')
                if len(partes) == 3:
                    nombre, ruc, nombre_usuario = partes
                    rucs[nombre] = (ruc, nombre_usuario)
                else:
                    print(f"Línea malformada: {linea}")
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return rucs, meses_opciones


def calcular_hash(archivo):
    with open(archivo, 'rb') as f:
        contenido = f.read()
        return hashlib.sha256(contenido).hexdigest()


def encontrar_y_eliminar_duplicados(directorio):
    hashes = {}
    duplicados = []
    mensajes = []

    for archivo in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, archivo)
        if os.path.isfile(ruta_completa) and archivo.endswith('.xml'):
            hash_archivo = calcular_hash(ruta_completa)
            if hash_archivo in hashes:
                duplicados.append(archivo)
            else:
                hashes[hash_archivo] = archivo

    mensajes.append(f'Se han eliminado {len(duplicados)} archivos duplicados.')
    return mensajes


def organizar_archivos_xml(directorio, opcion_nomenclatura, ruc_procesado, mes_seleccionado, tipo_documento):
    mensajes = []
    for archivo in os.listdir(directorio):
        if archivo.endswith('.xml'):
            ruta_archivo = os.path.join(directorio, archivo)
            documento = procesar_archivo_xml(ruta_archivo)
            if documento is not None:
                tipo = extraer_tipo(documento)
                ruc_receptor = extraer_ruc_receptor(documento, tipo)
                ruc_emisor = extraer_ruc_emisor(documento)
                clave_acceso = extraer_clave_autorizacion(documento)
                secuencial = extraer_secuencial(documento)
                anio, mes, _ = extraer_fecha(documento, tipo)
                if mes_seleccionado == "00" or mes == mes_seleccionado:
                    if tipo_documento == 'recibidos' and ruc_procesado == ruc_receptor:
                        destino_ruta = os.path.join(directorio, anio, mes, ruc_procesado, tipo_documento, 'xml',
                                                    tipo)
                        if opcion_nomenclatura == 'clave_de_acceso':
                            nombre_archivo = clave_acceso + '.xml'
                        else:
                            nombre_archivo = ruc_emisor + '_' + secuencial + '.xml'
                    elif tipo_documento == 'emitidos' and ruc_procesado == ruc_emisor:
                        destino_ruta = os.path.join(directorio, anio, mes, ruc_procesado, tipo_documento, 'xml',
                                                    tipo)
                        if opcion_nomenclatura == 'clave_de_acceso':
                            nombre_archivo = clave_acceso + '.xml'
                        else:
                            nombre_archivo = ruc_receptor + '_' + secuencial + '.xml'
                    else:
                        destino_ruta = directorio
                        nombre_archivo = clave_acceso + '.xml'
                    os.makedirs(destino_ruta, exist_ok=True)
                    destino_archivo = os.path.join(destino_ruta, nombre_archivo)
                    shutil.move(ruta_archivo, destino_archivo)
            else:
                mensajes.append(f'Error al procesar el archivo {archivo}. No se pudo extraer la información necesaria.')
    mensajes.append(f'Se han ordenado todos los archivos correctamente leidos, en las carpetas correspondientes.')

    return mensajes


def seleccionar_carpeta_ordenar(opcion_nomenclatura, rucs_opciones, meses_opciones, ruc_seleccionado, mes_seleccionado,
                                tipo_documento):
    directorio = filedialog.askdirectory()
    if directorio:
        mensajes = encontrar_y_eliminar_duplicados(directorio)
        ruc_valor, _ = rucs_opciones[ruc_seleccionado.get()]
        mes_valor = meses_opciones[mes_seleccionado.get()]
        mensajes += organizar_archivos_xml(directorio, opcion_nomenclatura, ruc_valor, mes_valor, tipo_documento)
        mostrar_mensaje("Resultado", "\n".join(mensajes))