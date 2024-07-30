import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from librerias.auxiliares import centrar_ventana
from librerias.funciones_excel import guardar_documentos_emitidos
from librerias.manejo_archivos import procesar_archivo_xml


def crear_ventana_progreso():
    """
    Crea y muestra una ventana de progreso que indica al usuario el progreso de una operación de largo tiempo.
    Retorna los componentes de la ventana para poder actualizarlos externamente.
    """
    progress_window = tk.Toplevel()  # Crea una ventana secundaria
    progress_window.title("Progreso")  # Establece el título de la ventana
    centrar_ventana(progress_window)  # Centra la ventana usando la función definida previamente

    # Crea y añade una etiqueta para mostrar mensajes de estado
    progress_label = tk.Label(progress_window, text="Iniciando...")
    progress_label.pack(pady=10)

    # Crea una variable DoubleVar para almacenar el porcentaje de progreso
    progress_var = tk.DoubleVar()
    # Crea y añade una barra de progreso que se vincula a la variable progress_var
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(padx=20, pady=10, fill=tk.X, expand=True)

    # Crea y añade un botón para cerrar la ventana de progreso, inicialmente desactivado
    accept_btn = tk.Button(progress_window, text="Cerrar", command=progress_window.destroy)
    accept_btn.pack(pady=10)

    # Retorna los componentes de la ventana para su uso externo
    return progress_window, progress_label, progress_bar, progress_var, accept_btn


def actualizar_progreso(progress_var, progress_label, current, total):
    """
    Actualiza la ventana de progreso con el porcentaje actual basado en el número de documentos procesados.
    - progress_var: La variable asociada a la barra de progreso.
    - progress_label: La etiqueta que muestra el mensaje de progreso.
    - current: El número actual de documentos procesados.
    - total: El número total de documentos a procesar.
    """
    percent = (current / total) * 100  # Calcula el porcentaje de progreso
    progress_var.set(percent)  # Actualiza la barra de progreso
    progress_label.config(text=f"Procesado: {current}/{total} documentos ({percent:.2f}%).")  # Actualiza el texto de la etiqueta


def seleccionar_raiz():
    """
    Maneja la selección de una carpeta conteniendo múltiples archivos XML. Procesa todos los archivos XML encontrados en la carpeta seleccionada.
    """
    documentos_procesados = []
    folder_path = filedialog.askdirectory(title="Seleccione la carpeta con los xml.")
    if folder_path:
        # Crear una lista de todos los archivos XML en el directorio y subdirectorios
        xml_files = []
        for root_dir, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.xml'):
                    xml_files.append(os.path.join(root_dir, file_name))

        total_files = len(xml_files)
        if total_files == 0:
            messagebox.showinfo("Información", "No se encontraron archivos XML en la carpeta seleccionada.")
            return

        # Crear y mostrar la ventana de progreso
        progress_window, progress_label, progress_bar, progress_var, accept_btn = crear_ventana_progreso()

        for index, file_path in enumerate(xml_files, start=1):
            file_path_abs = os.path.abspath(file_path)

            try:
                # Procesar el archivo XML con la ruta absoluta
                # CAMBIAR SI QUEREMOS HACERLO PARA UNIFACTOR por procesar_archivo_xml
                diccionario_documento = procesar_archivo_xml(file_path_abs)
                if diccionario_documento:
                    documentos_procesados.append(diccionario_documento)

                # Actualiza la barra de progreso y la etiqueta
                actualizar_progreso(progress_var, progress_label, index, total_files)
                progress_window.update()
            except (IndexError, ValueError):
                print(f"Error en la estructura de la ruta del archivo: {file_path_abs}")

        accept_btn.config(state='normal')

        # Guardar todos los documentos procesados en Excel una vez finalizado el procesamiento
        if documentos_procesados:
            # CAMBIAR SI QUEREMOS HACERLO PARA UNIFACTOR por guardar_documentos
            guardar_documentos_emitidos(documentos_procesados, folder_path + '/')
            # guardar_documentos(documentos_procesados, folder_path + '/')
    else:
        messagebox.showinfo("Cancelado", "No se seleccionó ninguna carpeta.")
