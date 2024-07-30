import tkinter as tk
from tkinter import messagebox, scrolledtext
from librerias.auxiliares import centrar_ventana
from sri_xml_bot.generar_reporte import seleccionar_raiz
from sri_xml_bot.imprimir_pdf import iniciar_impresion, seleccionar_carpeta_impresion
from sri_xml_bot.ordenar_xmls import cargar_rucs_desde_archivo, seleccionar_carpeta_ordenar
from sri_xml_bot.renombrar_xmls import actualizar_nombres_xml


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
    centrar_ventana(nueva_ventana)

    etiqueta_tipo_documento = tk.Label(nueva_ventana, text='Tipo de documento:')
    tipo_documento = tk.StringVar(value='recibidos')
    radio_documento_recibidos = tk.Radiobutton(nueva_ventana, text='Recibidos', variable=tipo_documento,
                                               value='recibidos')
    radio_documento_emitidos = tk.Radiobutton(nueva_ventana, text='Emitidos', variable=tipo_documento, value='emitidos')

    etiqueta_nomenclatura = tk.Label(nueva_ventana, text='Selecciona el formato de nombre de archivo:')
    opcion_nomenclatura = tk.StringVar(value='ruc_secuencial')
    radio_nomenclatura1 = tk.Radiobutton(nueva_ventana, text='Clave de acceso', variable=opcion_nomenclatura,
                                         value='clave_de_acceso')
    radio_nomenclatura2 = tk.Radiobutton(nueva_ventana, text='RUC emisor + Secuencial', variable=opcion_nomenclatura,
                                         value='ruc_secuencial')

    rucs_opciones, meses_opciones = cargar_rucs_desde_archivo()
    # Variable para almacenar la selección del RUC
    opcion_ruc = tk.StringVar(value=list(rucs_opciones.keys())[0])
    # Variable para almacenar la selección del mes
    opcion_mes = tk.StringVar(value=list(meses_opciones.keys())[0])

    # Crear menús de opción para RUC y mes
    etiqueta_ruc = tk.Label(nueva_ventana, text='Selecciona el RUC:')
    menu_ruc = tk.OptionMenu(nueva_ventana, opcion_ruc, *rucs_opciones.keys())
    etiqueta_mes = tk.Label(nueva_ventana, text='Selecciona el mes:')
    menu_mes = tk.OptionMenu(nueva_ventana, opcion_mes, *meses_opciones.keys())

    # Botón para seleccionar la carpeta
    boton_seleccionar = tk.Button(nueva_ventana, text='Seleccionar Carpeta',
                                  command=lambda: seleccionar_carpeta_ordenar(opcion_nomenclatura.get(), rucs_opciones,
                                                                              meses_opciones, opcion_ruc, opcion_mes,
                                                                              tipo_documento.get()))

    # Empaquetar los elementos en la ventana
    etiqueta_tipo_documento.pack()
    radio_documento_recibidos.pack()
    radio_documento_emitidos.pack()
    etiqueta_nomenclatura.pack()
    radio_nomenclatura1.pack()
    radio_nomenclatura2.pack()
    etiqueta_ruc.pack()
    menu_ruc.pack()
    etiqueta_mes.pack()
    menu_mes.pack()
    boton_seleccionar.pack(pady=10)


def generar_reporte(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Seleccionar Carpeta")
    centrar_ventana(nueva_ventana)
    label_temp = tk.Label(nueva_ventana, text='Seleccionar Carpeta Raiz para Ordenar Documentos.')
    label_temp.pack(pady=20)
    btn_select_folder = tk.Button(nueva_ventana, text="Seleccionar Carpeta", command=seleccionar_raiz)
    btn_select_folder.pack(pady=20)


def generar_pdf(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Ordenar Documentos")


def imprimir_pdf(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Imprimir PDF")
    centrar_ventana(nueva_ventana)

    # Crear entrada de texto para la ruta de la carpeta
    entrada_carpeta = tk.Entry(nueva_ventana, width=50)
    entrada_carpeta.pack()

    # Botón para seleccionar la carpeta
    btn_seleccionar_carpeta = tk.Button(nueva_ventana, text="Seleccionar Carpeta",
                                        command=lambda: seleccionar_carpeta_impresion(entrada_carpeta, nueva_ventana))
    btn_seleccionar_carpeta.pack()

    # Crear área de texto con barra de desplazamiento para ingresar nombres de archivos
    txt_nombres_archivos = scrolledtext.ScrolledText(nueva_ventana, height=10)
    txt_nombres_archivos.pack()

    # Botón para iniciar la impresión de archivos
    btn_imprimir = tk.Button(nueva_ventana, text="Imprimir Archivos",
                             command=lambda: iniciar_impresion(entrada_carpeta, txt_nombres_archivos, nueva_ventana))
    btn_imprimir.pack()


def renombrar_documentos(root):
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title('Renombrar XMLs y Eliminar Duplicados')
    centrar_ventana(nueva_ventana)
    etiqueta_nomenclatura = tk.Label(nueva_ventana, text='Selecciona el formato de nombre de archivo:')
    opcion_nomenclatura = tk.StringVar(value='ruc_secuencial')
    radio_nomenclatura1 = tk.Radiobutton(nueva_ventana, text='Clave de acceso', variable=opcion_nomenclatura,
                                         value='clave_de_acceso')
    radio_nomenclatura2 = tk.Radiobutton(nueva_ventana, text='RUC emisor + Secuencial', variable=opcion_nomenclatura,
                                         value='ruc_secuencial')
    boton_actualizar_nombres = tk.Button(nueva_ventana, text='Actualizar Nombres XML')
    etiqueta_nomenclatura.pack()
    radio_nomenclatura1.pack()
    radio_nomenclatura2.pack()
    # Botón para actualizar nombres de archivos XML, colocado al final
    boton_actualizar_nombres.pack(pady=10)
    # Asignación del comando al botón con los parámetros adecuados
    boton_actualizar_nombres['command'] = lambda: actualizar_nombres_xml(opcion_nomenclatura.get(), root)
    # Ejecutar el bucle principal de la aplicación
    nueva_ventana.mainloop()


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
