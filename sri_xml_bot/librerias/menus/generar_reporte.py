import os
import threading
import logging
from tkinter import Toplevel, Label, ttk, messagebox
from sri_xml_bot.librerias.utils import centrar_ventana
from sri_xml_bot.librerias.utils_excel import guardar_documentos_emitidos
from sri_xml_bot.librerias.utils_xml import procesar_archivo_xml

def generar_reporte_xlxs(parent, directorio):
    """
    Genera un reporte Excel a partir de los XML en el directorio dado,
    mostrando una ventana de progreso como diálogo modal.

    Args:
        parent (tk.Widget): Ventana padre para la modal.
        directorio (str): Directorio raíz donde se buscarán los XML.

    Returns:
        None: El resultado final (ruta del archivo generado o error)
              se muestra mediante MessageBox.
    """
    # 1) Validar que el directorio exista
    if not os.path.isdir(directorio):
        raise ValueError(f"El directorio no existe: {directorio}")

    # 2) Recorrer recursivamente y recopilar rutas absolutas de XML
    archivos = []
    for raiz, _, archivos_en_carpeta in os.walk(directorio):
        for nombre_fichero in archivos_en_carpeta:
            if nombre_fichero.lower().endswith('.xml'):
                ruta_completa = os.path.join(raiz, nombre_fichero)
                archivos.append(ruta_completa)

    total = len(archivos)
    if total == 0:
        # No hay archivos XML: abortar con excepción
        raise ValueError("No se encontraron archivos XML en el directorio.")

    # 3) Crear ventana de progreso como Toplevel modal
    ventana = Toplevel(parent)
    ventana.transient(parent)      # Se comporta como diálogo de la ventana padre
    ventana.grab_set()             # Bloquea interacción con la ventana principal
    centrar_ventana("Generando Reporte", ventana, ancho=400, alto=150)

    # 4) Widgets de estado y barra de progreso
    label_estado = Label(ventana, text="Iniciando generación de reporte...")
    label_estado.pack(pady=10)

    progress = ttk.Progressbar(ventana, orient="horizontal", mode="determinate", maximum=total)
    progress.pack(fill="x", padx=20, pady=10)

    def _procesar():
        documentos_procesados = []  # Almacena datos resultantes de cada XML

        try:
            # 5) Iterar cada XML, procesar y actualizar barra
            for idx, ruta in enumerate(archivos, start=1):
                # Nombre corto para mostrar en la barra
                nombre = os.path.basename(ruta)
                try:
                    # Llamada a función de procesamiento de XML
                    dic_doc = procesar_archivo_xml(ruta)
                    if dic_doc:
                        documentos_procesados.append(dic_doc)
                except Exception as e_xml:
                    # Loguear error específico de un XML y continuar
                    logging.exception(f"Error al procesar XML {ruta}: {e_xml}")

                # Actualizar progreso en GUI
                progress["value"] = idx
                label_estado.config(text=f"Procesando {idx}/{total}: {nombre}")
                ventana.update_idletasks()

                # Pausa breve para percibir el avance
                time.sleep(0.1)

            # 6) Si hay documentos procesados, generar el Excel
            if documentos_procesados:
                # La función guarda y retorna la ruta de salida internamente
                ruta_salida = guardar_documentos_emitidos(documentos_procesados, directorio + os.sep)
                # Notificar al usuario con MessageBox
                messagebox.showinfo("Proceso Completado", f"Reporte generado:\n{ruta_salida}", parent=parent)
            else:
                # No se procesó ningún XML válido
                messagebox.showwarning("Sin datos", "No se generó ningún documento. Verifica tus XML.", parent=parent)

        except Exception as e_general:
            # Captura de errores inesperados en _todo el proceso
            logging.exception(f"Error durante la generación del reporte: {e_general}")
            messagebox.showerror("Error", f"Ha ocurrido un error inesperado:\n{e_general}", parent=parent)
        finally:
            # 7) Cerrar siempre la ventana de progreso al finalizar
            ventana.destroy()

    # 8) Ejecutar la tarea en hilo separado (daemon para no bloquear el cierre)
    threading.Thread(target=_procesar, daemon=True).start()
