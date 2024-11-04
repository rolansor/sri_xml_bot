import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Button, StringVar, Checkbutton, IntVar, OptionMenu
from PIL import Image, ImageTk
import logging
from datetime import datetime
from sri_xml_bot.descargar_documentos import descargar_documentos
from sri_xml_bot.generar_pdfs import generar_pdfs
from sri_xml_bot.generar_reporte import generar_reporte
from sri_xml_bot.imprimir_pdfs import imprimir_pdfs
from sri_xml_bot.librerias.utils import centrar_ventana, ruta_relativa_recurso
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

        # Configurar el fondo de la ventana
        self.configurar_fondo()

        # Crear el menú principal
        self.crear_menu()

    def configurar_fondo(self):
        """
        Configura una imagen de fondo centrada en la ventana principal.
        """
        # Ruta del logo
        logo_path = ruta_relativa_recurso("archivos/logo.png")

        # Cargar la imagen
        imagen = Image.open(logo_path)
        imagen = imagen.resize((400, 300), Image.ANTIALIAS)  # Redimensionar para ajustarse
        self.imagen_fondo = ImageTk.PhotoImage(imagen)

        # Crear un Canvas para poner la imagen de fondo
        self.canvas = tk.Canvas(self.root, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)

        # Colocar la imagen en el centro del canvas
        self.canvas.create_image(400, 250, image=self.imagen_fondo)  # Centrada en (400, 250)

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
        Lee el archivo de datos y muestra una ventana secundaria para seleccionar un registro.
        """
        # Ruta al archivo de datos
        archivo_path = ruta_relativa_recurso("archivos/rucs.txt", filetypes=[("Archivos de texto", "*.txt")])

        # Leer el archivo y cargar los datos en una lista de tuplas
        datos = []
        try:
            with open(archivo_path, 'r') as file:
                for linea in file:
                    nombre, ruc, clave = linea.strip().split(',')
                    datos.append((nombre, ruc, clave))
            logging.info("Datos cargados correctamente desde el archivo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}", parent=self.root)
            logging.exception("Error al leer el archivo.")
            return

        # Abrir una ventana secundaria para mostrar la lista de opciones
        self.ventana_seleccion = Toplevel(self.root)
        self.ventana_seleccion.title("Seleccionar Cliente")
        centrar_ventana(self.ventana_seleccion, ancho=400, alto=250)
        self.ventana_seleccion.resizable(False, False)

        # Evitar interacción con la ventana principal hasta cerrar esta
        self.ventana_seleccion.grab_set()
        self.ventana_seleccion.transient(self.root)  # Asegura que se mantenga sobre la ventana principal

        # Listbox para mostrar nombre y RUC
        listbox = tk.Listbox(self.ventana_seleccion, width=50, height=10)
        listbox.pack(pady=20)
        # Llenar el Listbox con los nombres y RUCs
        for nombre, ruc, _ in datos:
            listbox.insert(tk.END, f"{nombre} - {ruc}")

        # Botón para seleccionar el elemento
        seleccionar_btn = Button(
            self.ventana_seleccion, text="Seleccionar",
            command=lambda: self.mostrar_opciones(datos, listbox.curselection())
        )
        seleccionar_btn.pack(pady=10)

    def mostrar_opciones(self, datos, seleccion):
        if not seleccion:
            messagebox.showwarning("Selección inválida", "Por favor, seleccione un elemento de la lista.", parent=self.ventana_seleccion)
            return

        indice = seleccion[0]
        nombre, ruc, clave = datos[indice]

        ventana_opciones = Toplevel(self.ventana_seleccion)
        ventana_opciones.title(f"Opciones de Descarga para {nombre}")
        centrar_ventana(ventana_opciones, ancho=400, alto=400)
        ventana_opciones.resizable(False, False)
        ventana_opciones.grab_set()  # Bloquear interacción con la ventana de selección hasta que se cierre
        ventana_opciones.transient(self.ventana_seleccion)

        # Etiquetas y listas desplegables para selección de fecha
        tk.Label(ventana_opciones, text="Introduce la fecha correspondiente:").pack(pady=5)

        # Año
        anioactual = datetime.now().year
        anios = [str(year) for year in range(anioactual - 10, anioactual + 1)]
        tk.Label(ventana_opciones, text="Año:").pack()
        year_var = StringVar(value=str(anioactual))
        year_menu = OptionMenu(ventana_opciones, year_var, *anios)
        year_menu.pack()

        # Mes
        mes_actual = str(datetime.now().month)
        tk.Label(ventana_opciones, text="Mes:").pack()
        month_var = StringVar(value=mes_actual)
        month_menu = OptionMenu(ventana_opciones, month_var, *[str(i) for i in range(1, 13)])
        month_menu.pack()

        # Día
        tk.Label(ventana_opciones, text="Día:").pack()
        day_var = StringVar(value="Todos")
        day_menu = OptionMenu(ventana_opciones, day_var, "Todos", *[str(i) for i in range(1, 32)])
        day_menu.pack()

        # Tipo de Descarga
        tipo_descarga_opciones = {"XML": "1", "PDF": "2", "Ambos": "0"}
        tk.Label(ventana_opciones, text="Tipo de descarga:").pack()
        tipo_descarga_var = StringVar(value="XML")  # Valor visible por defecto
        tipo_descarga_menu = OptionMenu(ventana_opciones, tipo_descarga_var, *tipo_descarga_opciones.keys())
        tipo_descarga_menu.pack()

        # Sección de tipo de documentos con checkboxes
        tk.Label(ventana_opciones, text="Elige el tipo de Documento:").pack(pady=10)

        tipos_documento = {
            "Factura": "1",
            "Liquidación de compra de bienes y prestación de servicios": "2",
            "Notas de Crédito": "3",
            "Notas de Débito": "4",
            "Comprobante de Retención": "6",
            "Todos los documentos": "0",
        }
        documento_var = StringVar(value="Factura")
        documento_menu = OptionMenu(ventana_opciones, documento_var, *tipos_documento.keys())
        documento_menu.pack()

        # Botón de aceptar con estilo
        aceptar_btn = Button(
            ventana_opciones, text="Aceptar",
            command=lambda: self.procesar_seleccion(
                year_var, month_var, day_var, tipo_descarga_var, documento_var, tipo_descarga_opciones, tipos_documento,
                ruc, clave), bg="#007BFF", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
        aceptar_btn.pack(pady=20)

    def procesar_seleccion(self, year_var, month_var, day_var, tipo_descarga_var, documento_var, tipo_descarga_opciones,
                           tipos_documento, ruc, clave):
        # Obtener el valor seleccionado en el Tipo de Descarga
        tipo_descarga = tipo_descarga_opciones[tipo_descarga_var.get()]

        # Obtener el valor seleccionado en Tipo de Documento
        tipo_documento = tipos_documento[documento_var.get()]

        # Obtener los valores de año, mes y día
        year = year_var.get()
        month = month_var.get()
        day = day_var.get()

        # Llamar a la función de descarga con los parámetros seleccionados
        descargar_documentos(year, month, day, tipo_descarga, tipo_documento, ruc, clave)

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
