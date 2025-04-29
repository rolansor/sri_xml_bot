import os
import datetime
from tkinter import Toplevel, Label, ttk
from openpyxl import Workbook
from sri_xml_bot.librerias.utils import centrar_ventana

def generar_reporte(directorio):
    """
    Genera un reporte Excel a partir de los XML/archivos en el directorio dado,
    mostrando una ventana de progreso utilizando utilidades compartidas.

    Args:
        directorio (str): Directorio raíz donde se procesarán los documentos.

    Returns:
        str: Ruta del archivo Excel generado.
    """
    # Recolectar archivos a procesar
    archivos = []
    for root, dirs, files in os.walk(directorio):
        for f in files:
            if f.lower().endswith('.xml'):
                archivos.append(os.path.join(root, f))
    total = len(archivos)
    if total == 0:
        raise ValueError("No se encontraron archivos para generar el reporte.")

    # Crear ventana de progreso y centrarla
    ventana_prog = Toplevel()
    centrar_ventana("Generando Reporte", ventana_prog, ancho=400, alto=150)
    Label(ventana_prog, text="Procesando archivos...").pack(pady=10)
    progress = ttk.Progressbar(ventana_prog, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10, padx=20)
    ventana_prog.update()

    # Crear workbook y hoja de cálculo
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    # Escribir encabezados
    headers = ["Nombre Archivo", "Fecha", "Tamaño (KB)", "Ruta Relativa"]
    ws.append(headers)

    # Procesar cada archivo y actualizar progreso
    for idx, ruta in enumerate(archivos, start=1):
        nombre = os.path.basename(ruta)
        stats = os.stat(ruta)
        fecha = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        tam_kb = round(stats.st_size / 1024, 2)
        ruta_rel = os.path.relpath(ruta, directorio)
        ws.append([nombre, fecha, tam_kb, ruta_rel])

        progress['value'] = (idx / total) * 100
        ventana_prog.update()

    # Guardar el archivo Excel con timestamp
    ahora = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_salida = f"reporte_{ahora}.xlsx"
    ruta_salida = os.path.join(directorio, nombre_salida)
    wb.save(ruta_salida)

    # Cerrar ventana de progreso
    ventana_prog.destroy()
    return ruta_salida