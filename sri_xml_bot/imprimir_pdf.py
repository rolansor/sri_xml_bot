import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import win32print
import win32api


def imprimir_archivo(impresora, ruta_archivo):
    # Imprime el archivo PDF en la impresora especificada
    win32api.ShellExecute(0, "print", ruta_archivo, f'/d:"{impresora}"', ".", 0)


def imprimir_archivos(carpeta, lista_de_archivos):
    impresora_predeterminada = win32print.GetDefaultPrinter()
    archivos_no_encontrados = []
    for nombre_archivo in lista_de_archivos:
        ruta_completa = os.path.join(carpeta, f"{nombre_archivo}.pdf")
        if os.path.exists(ruta_completa):
            imprimir_archivo(impresora_predeterminada, ruta_completa)
        else:
            archivos_no_encontrados.append(nombre_archivo)

    if archivos_no_encontrados:
        messagebox.showwarning(
            "Advertencia",
            "Los siguientes archivos no se encontraron y no se pudieron imprimir:\n" +
            "\n".join(archivos_no_encontrados)
        )
    else:
        messagebox.showinfo("Éxito", "Todos los archivos han sido enviados a la impresora.")


def seleccionar_carpeta_impresion(entrada_carpeta, ventana):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entrada_carpeta.delete(0, tk.END)
        entrada_carpeta.insert(0, folder_selected)
        ventana.lift()


def iniciar_impresion(entrada_carpeta, txt_nombres_archivos, ventana):
    carpeta = entrada_carpeta.get()
    nombres_archivos = txt_nombres_archivos.get("1.0", tk.END).strip().replace(" ","").split("\n")
    imprimir_archivos(carpeta, nombres_archivos)
    ventana.lift()
