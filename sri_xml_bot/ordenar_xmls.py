import os
import shutil
from tkinter import filedialog, messagebox
from librerias.leer_xmls import procesar_archivo_xml, extraer_tipo, extraer_ruc_receptor, extraer_ruc_emisor, \
    extraer_clave_autorizacion, extraer_secuencial, extraer_fecha
from librerias.manejo_archivos import encontrar_y_eliminar_duplicados


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
    # Mostrar el cuadro de diálogo para seleccionar el directorio
    directorio = filedialog.askdirectory()
    if directorio:
        # Acceder al RUC correspondiente usando el nombre seleccionado
        ruc_valor = rucs_opciones[ruc_seleccionado.get()]
        mes_valor = meses_opciones[mes_seleccionado.get()]

        # Realizar las operaciones necesarias con el directorio y los valores seleccionados
        mensajes = encontrar_y_eliminar_duplicados(directorio)
        mensajes += organizar_archivos_xml(directorio, opcion_nomenclatura, ruc_valor, mes_valor, tipo_documento)

        # Mostrar el resultado
        messagebox.showinfo("Resultado", "\n".join(mensajes))

