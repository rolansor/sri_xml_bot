import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from librerias.auxiliares import centrar_ventana, cerrar_ventana_secundaria, cerrar_aplicacion, \
    abrir_ventana_secundaria, cargar_rucs
from sri_xml_bot.generar_reporte import seleccionar_raiz
from sri_xml_bot.imprimir_pdf import iniciar_impresion, seleccionar_carpeta_impresion
from sri_xml_bot.licencia import verificar_licencia
from sri_xml_bot.ordenar_xmls import seleccionar_carpeta_ordenar
from sri_xml_bot.renombrar_xmls import actualizar_nombres_xml
from sri_xml_bot.robot_logica import pedir_opcion_centrada, pedir_fecha, configurar_webdriver, \
    iniciar_sesion, seleccionar_opciones_de_consulta, click_consulta, actualizar_excel, descargar_comprobantes, \
    navegar_a_la_pagina_siguiente, comparar_registros
from sri_xml_bot.xml_a_pdf import mostrar_progreso, procesar_xml_pdf, seleccionar_carpeta_topdf


# Funciones para cada opción
def descargar_documentos(root, rucs):

    # Convertir rucs en opciones para mostrar solo el nombre y el RUC en el menú
    opciones_ruc = {index: f"{data['nombre']} ({data['ruc']})" for index, data in rucs.items()}

    opcion, nueva_ventana = pedir_opcion_centrada("RUC", root, "Por favor, elige el RUC que deseas procesar:", opciones_ruc)

    # Si no se seleccionó ninguna opción, cerrar la ventana secundaria
    if not opcion:
        cerrar_ventana_secundaria(nueva_ventana, root)
        return

    # Obtener datos del RUC seleccionado
    usuario = rucs[int(opcion)]['ruc']
    contrasena = rucs[int(opcion)]['contrasena']

    tipos_documento = {
        "Factura": "Factura",
        "Liquidación de compra de bienes y prestación de servicios": "Liquidación de compra de bienes y prestación de servicios",
        "Notas de Crédito": "Notas de Crédito",
        "Notas de Débito": "Notas de Débito",
        "Comprobante de Retención": "Comprobante de Retención",
    }

    tipo_documento, nueva_ventana = pedir_opcion_centrada("Tipo de Documento", root,
                                           "Por favor, elige el tipo de Documento que deseas descargar:",
                                           tipos_documento)

    if not tipo_documento:
        cerrar_ventana_secundaria(nueva_ventana, root)
        return

    anio_actual = str(datetime.datetime.now().year)
    anios = {str(i): str(i) for i in range(2020, int(anio_actual) + 1)}
    mes_opciones = {str(i): str(i) for i in range(1, 13)}
    dia_opciones = {str(i): str(i) for i in range(1, 32)}

    anio, mes, dia, tipo_descarga, nueva_ventana = pedir_fecha("Fecha", root, "Introduce la fecha correspondiente:", anios,
                                                mes_opciones,
                                                dia_opciones)

    if not anio or not mes or not dia or not tipo_descarga:
        cerrar_ventana_secundaria(nueva_ventana, root)
        return

    # Mostrar la ventana principal de nuevo y continuar el proceso de descarga
    cerrar_ventana_secundaria(nueva_ventana, root)

    driver = configurar_webdriver()
    iniciar_sesion(driver, usuario, contrasena)
    seleccionar_opciones_de_consulta(driver, anio, mes, dia, tipo_documento)
    click_consulta(driver)
    while True:
        registros_a_descargar = comparar_registros(driver, usuario, anio, mes)
        filas_procesadas = descargar_comprobantes(driver, tipo_descarga, registros_a_descargar)
        actualizar_excel(usuario, anio, mes, filas_procesadas)
        if not navegar_a_la_pagina_siguiente(driver):
            break


def ordenar_documentos(root, rucs):
    """
    Abre una ventana secundaria para ordenar documentos, permitiendo al usuario seleccionar
    el tipo de documento, formato de nomenclatura y otros parámetros.
    """
    # Abre la ventana secundaria usando la función auxiliar para abrir ventanas
    nueva_ventana = abrir_ventana_secundaria("Ordenar Documentos", root, cerrar_ventana_secundaria)

    # Crear y empaquetar los widgets en la ventana secundaria
    etiqueta_tipo_documento = tk.Label(nueva_ventana, text='Tipo de documento:')
    tipo_documento = tk.StringVar(value='recibidos')

    # Radio buttons para seleccionar el tipo de documento
    radio_documento_recibidos = tk.Radiobutton(nueva_ventana, text='Recibidos', variable=tipo_documento, value='recibidos')
    radio_documento_emitidos = tk.Radiobutton(nueva_ventana, text='Emitidos', variable=tipo_documento, value='emitidos')

    etiqueta_nomenclatura = tk.Label(nueva_ventana, text='Selecciona el formato de nombre de archivo:')
    opcion_nomenclatura = tk.StringVar(value='ruc_secuencial')

    # Radio buttons para seleccionar el formato de nomenclatura
    radio_nomenclatura1 = tk.Radiobutton(nueva_ventana, text='Clave de acceso', variable=opcion_nomenclatura, value='clave_de_acceso')
    radio_nomenclatura2 = tk.Radiobutton(nueva_ventana, text='RUC emisor + Secuencial', variable=opcion_nomenclatura, value='ruc_secuencial')

    # Opciones para los meses
    meses_opciones = {
        "Todos": "00", "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05",
        "Junio": "06", "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10",
        "Noviembre": "11", "Diciembre": "12"
    }

    # Crear opciones para mostrar solo el nombre y RUC
    opciones_ruc = {f"{data['nombre']}": data['ruc'] for index, data in rucs.items()}

    # Variables para almacenar la selección del RUC y Mes
    opcion_ruc = tk.StringVar(value=list(opciones_ruc.keys())[0])
    opcion_mes = tk.StringVar(value=list(meses_opciones.keys())[0])

    # Crear menús de selección para RUC y Mes
    etiqueta_ruc = tk.Label(nueva_ventana, text='Selecciona el RUC:')
    menu_ruc = tk.OptionMenu(nueva_ventana, opcion_ruc, *opciones_ruc.keys())

    etiqueta_mes = tk.Label(nueva_ventana, text='Selecciona el mes:')
    menu_mes = tk.OptionMenu(nueva_ventana, opcion_mes, *meses_opciones.keys())

    # Botón para ejecutar la selección de carpeta y aplicar las opciones seleccionadas
    boton_seleccionar = tk.Button(nueva_ventana, text='Seleccionar Carpeta',
                                  command=lambda: seleccionar_carpeta_ordenar(
                                      opcion_nomenclatura.get(), opciones_ruc, meses_opciones,
                                      opcion_ruc, opcion_mes, tipo_documento.get()
                                  ))

    # Empaquetar los elementos en la ventana (ordenados)
    etiqueta_tipo_documento.pack(pady=10)
    radio_documento_recibidos.pack()
    radio_documento_emitidos.pack()

    etiqueta_nomenclatura.pack(pady=10)
    radio_nomenclatura1.pack()
    radio_nomenclatura2.pack()

    etiqueta_ruc.pack(pady=10)
    menu_ruc.pack()

    etiqueta_mes.pack(pady=10)
    menu_mes.pack()

    boton_seleccionar.pack(pady=20)


def generar_pdf(root):
    # Seleccionar carpeta para procesar
    folder_path = seleccionar_carpeta_topdf()
    if not folder_path:
        print("No se seleccionó ninguna carpeta.")
        root.destroy()
        return

    root.deiconify()  # Mostrar la ventana de nuevo si es necesario

    # Mostrar la ventana de progreso
    progress_window, progress_label, progress_bar = mostrar_progreso()

    def finalizar_proceso():
        # Esta función se llama cuando se completa el hilo de procesamiento
        messagebox.showinfo("Procesamiento Terminado", "Se han terminado de procesar todos los PDFs.")

    def procesar():
        procesar_xml_pdf(progress_window, progress_label, progress_bar, folder_path)
        root.after(0, finalizar_proceso)  # Llama a finalizar_proceso desde el hilo principal de Tkinter

    # Iniciar el procesamiento de XML a PDF en un hilo separado
    main_thread = threading.Thread(target=procesar)
    main_thread.start()


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
    boton_actualizar_nombres['command'] = lambda: actualizar_nombres_xml(opcion_nomenclatura.get(), nueva_ventana)


def main():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Opciones Principales")
    centrar_ventana(root)
    rucs = cargar_rucs()  # Cargar los RUCs una vez al inicio

    # Crear un frame para centrar el contenido
    frame_principal = tk.Frame(root)
    frame_principal.place(relx=0.5, rely=0.5, anchor='center')

    # Ancho base para los botones
    boton_ancho = 25

    # Botón para "Descargar Documentos" que pasa rucs
    boton_descargar = tk.Button(frame_principal, text="Descargar Documentos", width=boton_ancho, command=lambda: descargar_documentos(root, rucs), bg="blue", fg="white")
    boton_descargar.pack(pady=10)

    # Botón para "Ordenar Documentos" que también pasa rucs
    boton_ordenar = tk.Button(frame_principal, text="Ordenar Documentos", width=boton_ancho, command=lambda: ordenar_documentos(root, rucs), bg="blue", fg="white")
    boton_ordenar.pack(pady=10)

    # Botón para "Generar Reporte" que no requiere rucs
    boton_generar_reporte = tk.Button(frame_principal, text="Generar Reporte", width=boton_ancho, command=lambda: seleccionar_raiz(root), bg="blue", fg="white")
    boton_generar_reporte.pack(pady=10)

    # Botón para "Generar PDF's" que no requiere rucs
    boton_generar_pdfs = tk.Button(frame_principal, text="Generar PDF's", width=boton_ancho, command=lambda: generar_pdf(root), bg="blue", fg="white")
    boton_generar_pdfs.pack(pady=10)

    # Botón para "Imprimir PDF's" que no requiere rucs
    boton_imprimir_pdfs = tk.Button(frame_principal, text="Imprimir PDF's", width=boton_ancho, command=lambda: imprimir_pdf(root), bg="blue", fg="white")
    boton_imprimir_pdfs.pack(pady=10)

    # Botón para "Renombrar Documentos" que no requiere rucs
    boton_renombrar = tk.Button(frame_principal, text="Renombrar Documentos", width=boton_ancho, command=lambda: renombrar_documentos(root), bg="blue", fg="white")
    boton_renombrar.pack(pady=10)

    # Botón de cerrar en rojo
    boton_cerrar = tk.Button(frame_principal, text="Cerrar", width=boton_ancho, command=lambda: cerrar_aplicacion(root), bg="red", fg="white")
    boton_cerrar.pack(pady=10)

    # Configurar para que la aplicación se cierre si se presiona la X
    root.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))

    # Iniciar el bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()
