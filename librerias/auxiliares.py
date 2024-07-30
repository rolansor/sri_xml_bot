import os
import sys
import tkinter as tk


# Función para centrar la ventana
def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho = 400
    alto = 400
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
    ventana.deiconify()


# Muestra un mensaje en una ventana formateada
def mostrar_mensaje(titulo, mensaje):
    mensaje_dialog = tk.Toplevel()
    mensaje_dialog.withdraw()
    mensaje_dialog.title(titulo)
    centrar_ventana(mensaje_dialog)
    tk.Label(mensaje_dialog, text=mensaje, wraplength=280).pack(pady=20)
    tk.Button(mensaje_dialog, text="Aceptar", command=mensaje_dialog.destroy).pack(pady=10)
    mensaje_dialog.deiconify()
    mensaje_dialog.mainloop()
