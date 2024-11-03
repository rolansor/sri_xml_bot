import os
import sys
from tkinter import Tk, messagebox, filedialog
import re
import pandas as pd


def centrar_ventana(ventana, ancho=800, alto=500):
    """
    Centra una ventana en la pantalla con un tamaño fijo.

    :param ventana: Instancia de Tkinter window (Tk o Toplevel).
    :param ancho: Ancho de la ventana.
    :param alto: Alto de la ventana.
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


# Función para obtener la ruta de un recurso, manejando el entorno de PyInstaller
def ruta_relativa_recurso(relativa, filetypes=[("Archivos de texto", "*.txt")]):
    """
    Retorna la ruta correcta de un recurso en el mismo directorio desde el que se ejecuta el .exe.
    Si no se encuentra, abre un diálogo para que el usuario seleccione el archivo manualmente.

    Args:
        relativa: La ruta relativa del recurso que se quiere acceder.
        filetypes: Lista de tuplas para filtrar el tipo de archivo en el cuadro de diálogo.

    Returns:
        str or None: La ruta absoluta del recurso o None si no se selecciona ningún archivo.
    """

    # Obtener el directorio de ejecución
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    ruta_archivo = os.path.join(base_dir, relativa)

    # Verificar si el archivo existe en la ubicación esperada
    while not os.path.exists(ruta_archivo):
        # Crear la ventana principal de Tk
        temporal = Tk()
        temporal.withdraw()  # Oculta la ventana principal de Tk
        file_name = os.path.basename(ruta_archivo)

        # Advertencia al usuario y opciones para seleccionar o cerrar la aplicación
        respuesta = messagebox.askretrycancel(
            "Archivo no encontrado",
            f"No se encontró el archivo {file_name}. ¿Desea intentar seleccionarlo manualmente?"
        )

        # Si el usuario cancela, se cierra la aplicación
        if not respuesta:
            messagebox.showinfo("Operación cancelada", "No se seleccionó ningún archivo. Cerrando aplicación.")
            temporal.destroy()
            sys.exit(1)

        # Permitir que el usuario seleccione el archivo manualmente
        ruta_archivo = filedialog.askopenfilename(
            title=f"Seleccione el archivo {file_name}",
            filetypes=filetypes,
            initialdir=base_dir
        )

        # Si el usuario no selecciona ningún archivo, se vuelve a mostrar la advertencia
        if not ruta_archivo:
            messagebox.showwarning("Selección inválida", "No seleccionó ningún archivo. Inténtelo de nuevo o cancele.")
            temporal.destroy()
        else:
            # Si selecciona un archivo, cerramos la ventana temporal y devolvemos la ruta
            temporal.destroy()
            break

    return ruta_archivo


def separar_tipo_y_serie(comprobante):
    """
    Separa el tipo y la serie del comprobante.
    """
    match = re.match(r"(.+?)\s+(\d{3}-\d{3}-\d{9})", comprobante)
    return (match.group(1).strip(), match.group(2).strip()) if match else (None, None)