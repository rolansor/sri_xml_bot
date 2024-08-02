import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import win32print
import win32api


def seleccionar_carpeta_impresion(entrada_carpeta, ventana):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entrada_carpeta.delete(0, tk.END)
        entrada_carpeta.insert(0, folder_selected)
        ventana.lift()


def imprimir_archivo(impresora, ruta_archivo):
    try:
        if not os.path.exists(ruta_archivo):
            return
        result = win32api.ShellExecute(0, "print", ruta_archivo, f'/d:"{impresora}"', ".", 0)
        if result <= 32:
            messagebox.showerror("Error de impresión", f"Error al intentar imprimir {ruta_archivo}. Código de error: {result}")
        else:
            time.sleep(1)
    except Exception as e:
        messagebox.showerror("Error de impresión", f"Se produjo un error al intentar imprimir {ruta_archivo}: {e}")


def imprimir_archivos_en_hilo(carpeta, lista_de_archivos):
    hilo_impresion = threading.Thread(target=imprimir_archivos, args=(carpeta, lista_de_archivos))
    hilo_impresion.start()


def imprimir_archivos(carpeta, lista_de_archivos):
    impresora_predeterminada = win32print.GetDefaultPrinter()
    archivos_no_encontrados = []
    archivos_impresos = 0

    for nombre_archivo in lista_de_archivos:
        ruta_completa = os.path.join(carpeta, f"{nombre_archivo}.pdf")
        if os.path.exists(ruta_completa):
            if imprimir_archivo(impresora_predeterminada, ruta_completa):
                archivos_impresos += 1
        else:
            archivos_no_encontrados.append(nombre_archivo)

    if archivos_no_encontrados:
        messagebox.showwarning(
            "Advertencia",
            "Los siguientes archivos no se encontraron y no se pudieron imprimir:\n" +
            "\n".join(archivos_no_encontrados)
        )
    if archivos_impresos > 0:
        messagebox.showinfo("Éxito", f"{archivos_impresos} archivo(s) han sido enviados a la impresora.")
    else:
        messagebox.showinfo("Información", "No se enviaron archivos a la impresora.")


def iniciar_impresion(entrada_carpeta, txt_nombres_archivos, ventana):
    carpeta = entrada_carpeta.get()
    nombres_archivos = txt_nombres_archivos.get("1.0", tk.END).strip().replace(" ","").split("\n")
    imprimir_archivos_en_hilo(carpeta, nombres_archivos)
    ventana.lift()
