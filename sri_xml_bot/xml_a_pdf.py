import sys
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from librerias.auxiliares import centrar_ventana
from librerias.leer_xmls import procesar_archivo_xml
from librerias.xml_a_pdf.ride_factura import imprimir_factura_pdf
from librerias.xml_a_pdf.ride_notacredito import imprimir_nc_pdf
from librerias.xml_a_pdf.ride_retencion import imprimir_retencion_pdf


def seleccionar_carpeta_topdf():
    """
    Permite al usuario elegir un directorio.
    Retorna:
        folder_path (str): La ruta del directorio seleccionado.
    """
    root = tk.Tk()
    root.withdraw()
    # Usuario elige seleccionar un directorio
    folder_path = filedialog.askdirectory(title="Seleccione la Carpeta donde están los XML.")
    root.destroy()
    return folder_path


def update_progress_window(window, label, progress_bar, message, value=None):
    """
    Actualiza el mensaje y el valor de la barra de progreso en una ventana de progreso.
    Parámetros:
        Window (Tk): Ventana de progreso a actualizar.
        Label (Label): Etiqueta dentro de la ventana que muestra el mensaje.
        progress_bar (Progressbar): Barra de progreso para mostrar el progreso.
        Message (str): Mensaje a mostrar.
        value (int): Valor para actualizar la barra de progreso.
    No retorna nada.
    """
    label.config(text=message)
    if value is not None:
        progress_bar['value'] = value
    window.update()


def mostrar_progreso():
    """
    Crea y muestra una ventana de progreso.
    No recibe parámetros.
    Retorna:
        tuple: Contiene la ventana de progreso, la etiqueta de texto y la barra de progreso dentro de ella.
    """
    window = tk.Toplevel()
    window.title("Progreso")
    centrar_ventana(window)
    label = tk.Label(window, text="Iniciando...")
    label.pack(padx=20, pady=10)
    progress_bar = ttk.Progressbar(window, orient='horizontal', length=250, mode='determinate')
    progress_bar.pack(padx=20, pady=10)
    return window, label, progress_bar


def seleccionar_funcion_impresion(tipo):
    return {
        'facturas': imprimir_factura_pdf,
        'comprobantes_de_retencion': imprimir_retencion_pdf,
        'notas_de_credito': imprimir_nc_pdf
    }[tipo]


def obtener_ruta_logo():
    """
    Devuelve la ruta del archivo del logo. Maneja correctamente la ruta tanto en modo desarrollo
    como en el ejecutable generado por PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        # Si está corriendo dentro de un ejecutable PyInstaller
        return os.path.join(sys._MEIPASS, 'xml_a_pdf/nologo.png')
    return os.path.join(os.path.dirname(__file__), 'librerias/xml_a_pdf/nologo.png')


def procesar_xml_pdf(progress_window, progress_label, progress_bar, folder_path):
    contador_xml = 0
    contador_pdf = 0
    ruta_logo = obtener_ruta_logo()
    # Verificación de existencia del archivo
    if not os.path.exists(ruta_logo):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio_actual, '../librerias/xml_a_pdf/nologo.png')

    # Contar el número total de archivos XML para la barra de progreso
    total_xml = sum(len(files) for _, _, files in os.walk(folder_path) if any(f.endswith('.xml') for f in files))

    for root_dir, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.xml'):
                contador_xml += 1
                progress_percentage = int((contador_xml / total_xml) * 100)
                update_progress_window(progress_window, progress_label, progress_bar,
                                       f"Procesando XML #{contador_xml} de {total_xml}", progress_percentage)

                file_path = os.path.join(root_dir, file_name)
                try:
                    diccionario_documento = procesar_archivo_xml(file_path)
                    clave_acceso = diccionario_documento['infoTributaria']['claveAcceso']
                    nombre_archivo_pdf = f"{clave_acceso}.pdf"

                    # Construye la nueva ruta para el archivo PDF
                    # Reemplaza '\xml\' en la ruta con '\pdf\' para mantener la estructura deseada
                    ruta_carpeta_pdf = root_dir.replace('\\xml', '\\pdf')
                    os.makedirs(ruta_carpeta_pdf, exist_ok=True)

                    ruta_archivo_pdf = os.path.join(ruta_carpeta_pdf, nombre_archivo_pdf)
                    contador_pdf += 1
                    update_progress_window(progress_window, progress_label, progress_bar,
                                           f"Generando PDF #{contador_pdf}", progress_percentage)

                    # Aquí llamarías a tu función de impresión PDF
                    funcion_impresion = seleccionar_funcion_impresion(
                        diccionario_documento['datos_extras']['tipoDocumento'])
                    funcion_impresion(diccionario_documento, ruta_archivo_pdf, ruta_logo)

                except (IndexError, KeyError) as e:
                    print(f"Error procesando archivo {file_name}: {e}")

    update_progress_window(progress_window, progress_label, progress_bar, "Proceso completado.", 100)
