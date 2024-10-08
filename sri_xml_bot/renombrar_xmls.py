import datetime
from tkinter import filedialog, messagebox
import os
import hashlib
import shutil
from librerias.leer_xmls import procesar_archivo_xml, extraer_clave_autorizacion, extraer_secuencial, \
    extraer_ruc_emisor, extraer_tipo, extraer_ruc_receptor
from librerias.manejo_archivos import encontrar_y_eliminar_duplicados


def actualizar_nombres_xml(opcion_nomenclatura, root):
    """
    Actualiza los nombres de los archivos XML en una estructura de directorios basándose en la opción
    de nomenclatura seleccionada por el usuario. Los archivos se renombran sin cambiar de ubicación.

    Parámetros:
    - opcion_nomenclatura (str): Opción de nomenclatura seleccionada por el usuario ('Clave de acceso' o 'RUC emisor + Secuencial').

    No retorna nada.
    """
    directorio = filedialog.askdirectory()
    if directorio:
        encontrar_y_eliminar_duplicados(directorio)
        contador_documentos = 0
        for raiz, _, archivos in os.walk(directorio):
            # Determinar si el archivo está en un directorio 'emitidos' o 'recibidos'
            tipo_documento = 'emitidos' if 'emitidos' in raiz else 'recibidos' if 'recibidos' in raiz else None
            for archivo in archivos:
                if archivo.endswith('.xml'):
                    ruta_completa = os.path.join(raiz, archivo)
                    documento = procesar_archivo_xml(ruta_completa)

                    if documento is not None:
                        clave_acceso = extraer_clave_autorizacion(documento)
                        secuencial = extraer_secuencial(documento)
                        ruc_emisor = extraer_ruc_emisor(documento)
                        tipo = extraer_tipo(documento)
                        ruc_receptor = extraer_ruc_receptor(documento,tipo)
                        if opcion_nomenclatura == 'clave_de_acceso':
                            nuevo_nombre = clave_acceso + '.xml'
                        else:
                            nuevo_nombre = "{}_{}.xml".format(
                                ruc_receptor if tipo_documento == 'emitidos' else ruc_emisor, secuencial)

                        nueva_ruta_completa = os.path.join(raiz, nuevo_nombre)

                        if ruta_completa != nueva_ruta_completa:
                            contador_documentos += 1
                            #print(f'#{contador_documentos} Documento Renombrado: {ruta_completa} a {nueva_ruta_completa}')
                            shutil.move(ruta_completa, nueva_ruta_completa)
                    else:
                        print(f'Error al procesar el archivo {archivo}. No se pudo extraer la información necesaria.')
        # Preguntar al usuario si desea cerrar la aplicación
        messagebox.showinfo("Finalizado", "El proceso ha terminado.")
        root.destroy()
