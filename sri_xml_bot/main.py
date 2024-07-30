import tkinter as tk
from tkinter import messagebox
from librerias.auxiliares import centrar_ventana


# Función para cerrar la aplicación
def cerrar_aplicacion(root):
    respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas salir?")
    if respuesta:
        root.destroy()


# Funciones para cada opción
def descargar_documentos(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def ordenar_documentos(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def generar_reporte(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def generar_pdf(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def imprimir_pdf(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def renombrar_documentos(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def main():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Opciones Principales")
    centrar_ventana(root)

    # Opciones principales
    opciones_principales = {
        "Descargar Documentos": descargar_documentos,
        "Ordenar Documentos": ordenar_documentos,
        "Generar Reporte": generar_reporte,
        "Generar PDF's": generar_pdf,
        "Imprimir PDF's": imprimir_pdf,
        "Renombrar Documentos": renombrar_documentos
    }

    # Crear un frame para centrar el contenido
    frame_principal = tk.Frame(root)
    frame_principal.place(relx=0.5, rely=0.5, anchor='center')

    # Calcular el ancho del botón más grande
    boton_max_ancho = max([len(texto) for texto in opciones_principales.keys()])

    # Crear los botones para cada opción con sus respectivas funciones en el frame centrado
    for texto, comando in opciones_principales.items():
        boton = tk.Button(frame_principal, text=texto, width=boton_max_ancho + 2,
                          command=lambda cmd=comando: cmd(root), bg="blue", fg="white")
        boton.pack(pady=10)

    # Crear el botón de cerrar en rojo en el frame centrado
    boton_cerrar = tk.Button(frame_principal, text="Cerrar", command=lambda: cerrar_aplicacion(root),
                             bg="red", fg="white", width=boton_max_ancho + 2)
    boton_cerrar.pack(pady=10)

    # Configurar para que la aplicación se cierre si se presiona la X
    root.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))

    # Iniciar el bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()
