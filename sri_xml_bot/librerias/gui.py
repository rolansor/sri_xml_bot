import tkinter as tk
from tkinter import messagebox
import logging
from sri_xml_bot.descargar_documentos import descargar_documentos
from sri_xml_bot.generar_pdfs import generar_pdfs
from sri_xml_bot.generar_reporte import generar_reporte
from sri_xml_bot.imprimir_pdfs import imprimir_pdfs
from sri_xml_bot.librerias.utils import centrar_ventana
from sri_xml_bot.ordenar_documentos import ordenar_documentos


class Application:
    def __init__(self):
        """
        Inicializa la aplicación y configura la ventana principal.
        """
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Documentos")
        centrar_ventana(self.root, ancho=800, alto=500)
        self.root.resizable(False, False)

        self.crear_menu()

    def crear_menu(self):
        """
        Crea el menú principal con todas las opciones.
        """
        menubar = tk.Menu(self.root)

        # Menú principal
        menu_principal = tk.Menu(menubar, tearoff=0)
        menu_principal.add_command(label="Descargar Documentos", command=self.descargar_documentos)
        menu_principal.add_command(label="Ordenar Documentos", command=self.ordenar_documentos)
        menu_principal.add_command(label="Generar Reporte", command=self.generar_reporte)
        menu_principal.add_command(label="Generar PDF's", command=self.generar_pdfs)
        menu_principal.add_command(label="Imprimir PDF's", command=self.imprimir_pdfs)
        menubar.add_cascade(label="Opciones", menu=menu_principal)

        # Menú Acerca de
        menu_acerca_de = tk.Menu(menubar, tearoff=0)
        menu_acerca_de.add_command(label="Detalles del Desarrollo", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Acerca de", menu=menu_acerca_de)

        self.root.config(menu=menubar)

    def descargar_documentos(self):
        """
        Maneja la opción de descargar documentos.
        """
        try:
            descargar_documentos()
            messagebox.showinfo("Éxito", "Documentos descargados correctamente.")
            logging.info("Documentos descargados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo descargar los documentos: {e}")
            logging.exception("Error al descargar documentos.")

    def ordenar_documentos(self):
        """
        Maneja la opción de ordenar documentos.
        """
        try:
            ordenar_documentos()
            messagebox.showinfo("Éxito", "Documentos ordenados correctamente.")
            logging.info("Documentos ordenados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ordenar los documentos: {e}")
            logging.exception("Error al ordenar documentos.")

    def generar_reporte(self):
        """
        Maneja la opción de generar reportes.
        """
        try:
            generar_reporte()
            messagebox.showinfo("Éxito", "Reporte generado correctamente.")
            logging.info("Reporte generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
            logging.exception("Error al generar reporte.")

    def generar_pdfs(self):
        """
        Maneja la opción de generar PDFs.
        """
        try:
            generar_pdfs()
            messagebox.showinfo("Éxito", "PDFs generados correctamente.")
            logging.info("PDFs generados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar los PDFs: {e}")
            logging.exception("Error al generar PDFs.")

    def imprimir_pdfs(self):
        """
        Maneja la opción de imprimir PDFs.
        """
        try:
            imprimir_pdfs()
            messagebox.showinfo("Éxito", "PDFs enviados a impresión correctamente.")
            logging.info("PDFs enviados a impresión exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir los PDFs: {e}")
            logging.exception("Error al imprimir PDFs.")


    def mostrar_acerca_de(self):
        """
        Muestra una ventana con detalles sobre el desarrollo de la aplicación.
        """
        detalles = (
            "Sistema de Gestión de Documentos\n"
            "Versión: 1.0\n"
            "Desarrollado por: Tu Nombre\n"
            "Fecha de Desarrollo: Abril 2024\n"
            "Tecnologías Utilizadas:\n"
            "- Python 3.7\n"
            "- Tkinter\n"
            "- Otras Librerías según corresponda"
        )
        messagebox.showinfo("Acerca de", detalles)
        logging.info("Información 'Acerca de' mostrada.")


    def run(self):
        """
        Ejecuta el bucle principal de la interfaz gráfica.
        """
        self.root.mainloop()
