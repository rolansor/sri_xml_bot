import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Button, StringVar, OptionMenu, filedialog, Label
from tkinter.constants import END
from PIL import Image, ImageTk
import logging
from datetime import datetime
from sri_xml_bot.descargar_documentos import descargar_documentos
from sri_xml_bot.generar_pdfs import generar_pdfs
from sri_xml_bot.generar_reporte import generar_reporte
from sri_xml_bot.imprimir_pdfs import imprimir_pdfs
from sri_xml_bot.librerias.utils import centrar_ventana, ruta_relativa_recurso, guardar_configuracion_ini, \
    cargar_configuracion_ini
from sri_xml_bot.ordenar_documentos import ordenar_documentos


class Application:
    def __init__(self):
        """
        Inicializa la aplicación y configura la ventana principal.
        """
        self.root = tk.Tk()
        centrar_ventana("Sistema de Gestión de Documentos", self.root, ancho=800, alto=500)

        # Cargar todas las configuraciones al inicio
        self.configuraciones = cargar_configuracion_ini()

        # Configurar el fondo de la ventana
        self.configurar_fondo()

        # Crear el menú principal
        self.crear_menu()

    def configurar_fondo(self):
        """
        Configura una imagen de fondo centrada en la ventana principal.
        """
        # Ruta del logo
        logo_path = ruta_relativa_recurso(self.configuraciones.get('ruta_logos'))

        # Cargar la imagen
        imagen = Image.open(logo_path)
        imagen = imagen.resize((400, 300), Image.ANTIALIAS)  # Redimensionar para ajustarse
        self.imagen_fondo = ImageTk.PhotoImage(imagen)

        # Crear un Canvas para poner la imagen de fondo
        self.canvas = tk.Canvas(self.root, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)

        # Colocar la imagen en el centro del canvas
        self.canvas.create_image(400, 250, image=self.imagen_fondo)  # Centrada en (400, 250)

        # Obtener el RUC seleccionado de las configuraciones
        ruc_seleccionado = self.configuraciones.get('ruc_actual')

        # Mostrar el RUC seleccionado en la parte inferior del Canvas
        self.canvas.create_text(
            400, 450,  # Coordenadas en el centro abajo de la imagen
            text=f"RUC SELECCIONADO: {ruc_seleccionado}",
            font=("Arial", 12, "bold"),
            fill="black"  # Color del texto
        )

    def crear_menu(self):
        """
        Crea el menú principal con todas las opciones.
        """
        menubar = tk.Menu(self.root)

        # Submenú de "Recibidos"
        menu_recibidos = tk.Menu(menubar, tearoff=0)
        menu_recibidos.add_command(label="Facturas", command=lambda: self.descargar_recibidos("1"))
        menu_recibidos.add_command(label="Notas de Crédito", command=lambda: self.descargar_recibidos("3"))
        menu_recibidos.add_command(label="Comprobantes de Retención", command=lambda: self.descargar_recibidos("6"))
        menu_recibidos.add_command(label="Notas de Débito", command=lambda: self.descargar_recibidos("4"))
        menu_recibidos.add_command(label="Liquidación de Compras", command=lambda: self.descargar_recibidos("2"))
        menu_recibidos.add_command(label="Todos", command=lambda: self.descargar_recibidos("0"))
        menubar.add_cascade(label="Recibidos", menu=menu_recibidos)

        # Submenú de "Emitidos"
        menu_emitidos = tk.Menu(menubar, tearoff=0)
        menu_emitidos.add_command(label="Facturas", command=lambda: self.descargar_emitidos("1"))
        menu_emitidos.add_command(label="Notas de Crédito", command=lambda: self.descargar_emitidos("3"))
        menu_emitidos.add_command(label="Comprobantes de Retención", command=lambda: self.descargar_emitidos("6"))
        menu_emitidos.add_command(label="Notas de Débito", command=lambda: self.descargar_emitidos("4"))
        menu_emitidos.add_command(label="Liquidación de Compras", command=lambda: self.descargar_emitidos("2"))
        menu_emitidos.add_command(label="Todos", command=lambda: self.descargar_emitidos("0"))
        menubar.add_cascade(label="Emitidos", menu=menu_emitidos)

        # Submenú de "Clasificar"
        menu_clasificar = tk.Menu(menubar, tearoff=0)
        menu_clasificar.add_command(label="Ordenar Documentos Recibidos", command=self.ordenar_documentos_recibidos)
        menu_clasificar.add_command(label="Ordenar Documentos Emitidos", command=self.ordenar_documentos_recibidos)
        menu_clasificar.add_command(label="Reorganizar Documentos", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Clasificar", menu=menu_clasificar)

        # Submenú de "Reportes"
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menu_reportes.add_command(label="Generar XLS", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Reportes", menu=menu_reportes)

        # Submenú de "PDFs"
        menu_pdfs = tk.Menu(menubar, tearoff=0)
        menu_pdfs.add_command(label="Generar PDFs", command=self.generar_pdfs)
        menu_pdfs.add_command(label="Configurar PDFs", command=self.generar_pdfs)
        menubar.add_cascade(label="PDFs", menu=menu_pdfs)

        # Menú "Configuraciones"
        menu_configuracion = tk.Menu(menubar, tearoff=0)
        menu_configuracion.add_command(label="Estructura de Rutas", command=self.configurar_ruta_guardado)
        menu_configuracion.add_command(label="Formato Nombre Archivo", command=self.configurar_nombre_guardado)
        menu_configuracion.add_command(label="Ruta Rucs", command=self.mostrar_acerca_de)
        menu_configuracion.add_command(label="RUC ACTUAL", command=self.mostrar_acerca_de)
        menu_configuracion.add_command(label="Ruta WebDriver", command=self.mostrar_acerca_de)
        menu_configuracion.add_command(label="Ruta Log", command=self.mostrar_acerca_de)
        menu_configuracion.add_command(label="Ruta Logo por defecto", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Configuraciones", menu=menu_configuracion)


        # Menú "Acerca de"
        menu_acerca_de = tk.Menu(menubar, tearoff=0)
        menu_acerca_de.add_command(label="Detalles del Desarrollo", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Acerca de", menu=menu_acerca_de)

        self.root.config(menu=menubar)

    def descargar_recibidos(self, tipo_documento):
        """
        Lee el archivo de datos y muestra una ventana secundaria para seleccionar un registro.
        """
        # Ruta al archivo de datos
        archivo_path = ruta_relativa_recurso(self.configuraciones.get('ruta_rucs'), filetypes=[("Archivos de texto", "*.txt")])

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
            command=lambda: self.mostrar_opciones(datos, tipo_documento, listbox.curselection())
        )
        seleccionar_btn.pack(pady=10)

    def mostrar_opciones(self, datos, tipo_documento, seleccion):
        if not seleccion:
            messagebox.showwarning("Selección inválida", "Por favor, seleccione un elemento de la lista.", parent=self.ventana_seleccion)
            return

        indice = seleccion[0]
        nombre, ruc, clave = datos[indice]

        ventana_opciones = Toplevel(self.ventana_seleccion)
        centrar_ventana(f"Opciones de Descarga para {nombre}", ventana_opciones, ancho=400, alto=400)
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

        # Botón de aceptar con estilo
        aceptar_btn = Button(
            ventana_opciones, text="Aceptar",
            command=lambda: descargar_documentos(self.configuraciones.get('ruta_chromedriver'),
                year_var.get(),
                month_var.get(),
                day_var.get(),
                tipo_descarga_opciones[tipo_descarga_var.get()],
                tipo_documento,
                ruc,
                clave
            ),
            bg="#007BFF", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5
        )
        aceptar_btn.pack(pady=20)

    def descargar_emitidos(self, tipo_documento):
        """
        Maneja la opción de ordenar documentos.
        """
        try:
            messagebox.showinfo("Éxito", "Documentos ordenados correctamente.")
            logging.info("Documentos ordenados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ordenar los documentos: {e}")
            logging.exception("Error al ordenar documentos.")

    def configurar_nombre_guardado(self):
        """
        Abre una ventana para configurar la estructura de nombres y la ruta de guardado para los archivos recibidos.
        """
        self.venta_configuracion_nombre = Toplevel(self.root)
        centrar_ventana("Configurar nombres XMLs", self.venta_configuracion_nombre, ancho=350, alto=450)

        # Evitar interacción con la ventana principal hasta cerrar esta
        self.venta_configuracion_nombre.grab_set()
        self.venta_configuracion_nombre.transient(self.root)

        # Crear un marco para centrar las opciones de nombre del archivo
        frame_nombre = tk.Frame(self.venta_configuracion_nombre)
        frame_nombre.pack(pady=10)

        # Etiqueta para el título de las opciones de nombre del archivo
        tk.Label(frame_nombre, text="Formato de Nombre del Archivo XML:").pack(pady=10)

        nombre_var = StringVar(value="clave_acceso")
        opciones_nombre = {
            "RUC Emisor + Secuencial": "ruc_secuencial",
            "Clave de Acceso": "clave_acceso",
            "Fecha + Secuencial": "fecha_secuencial"
        }

        # Crear los Radiobuttons dentro del marco y centrarlos
        for texto, valor in opciones_nombre.items():
            tk.Radiobutton(frame_nombre, text=texto, variable=nombre_var, value=valor).pack(anchor="center")


        # Guardar configuración
        def guardar_configuracion():
            # Obtener la selección de nombre de archivo
            nombre_archivo = nombre_var.get()
            # Cambiar solo la configuración 'nombre_archivo'
            guardar_configuracion_ini('nombre_archivo', nombre_archivo)
            # Cierra luego de guardar
            self.venta_configuracion_nombre.destroy()

        # Botón para guardar la configuración
        Button(self.venta_configuracion_nombre, text="Guardar Opción Nombre", command=guardar_configuracion).pack(pady=20)

    def configurar_ruta_guardado(self):
        """
        Abre una ventana para configurar la ruta de guardado para los archivos recibidos.
        """
        self.ventana_configuracion_ruta = Toplevel(self.root)
        centrar_ventana("Configurar Ruta de Archivos XMLs", self.ventana_configuracion_ruta, ancho=350, alto=450)

        # Evitar interacción con la ventana principal hasta cerrar esta
        self.ventana_configuracion_ruta.grab_set()
        self.ventana_configuracion_ruta.transient(self.root)

        # Crear un marco para centrar las opciones de nombre del archivo
        frame_nombre = tk.Frame(self.ventana_configuracion_ruta)
        frame_nombre.pack(pady=10)

        # Configurar ruta de guardado con Listbox reordenable
        tk.Label(self.ventana_configuracion_ruta, text="\nRuta de Guardado (Ordenable):").pack()

        ruta_opciones = ["Año", "Mes", "RUC", "Recibido/Emitido", "PDF/XML", "Tipo Documento"]

        abreviaciones_ruta = {
            "Año": "Año",
            "Mes": "Mes",
            "RUC": "RUC",
            "Recibido/Emitido": "RecEmi",
            "PDF/XML": "XML",
            "Tipo Documento": "TipoDocumento"
        }

        ruta_listbox = Listbox(self.ventana_configuracion_ruta, selectmode="single", width=30, height=len(ruta_opciones))
        for opcion in ruta_opciones:
            ruta_listbox.insert(END, opcion)
        ruta_listbox.pack(pady=10)

        # Funciones para reordenar la selección
        def mover_arriba():
            try:
                seleccion = ruta_listbox.curselection()
                if not seleccion or seleccion[0] == 0:
                    return
                index = seleccion[0]
                valor = ruta_listbox.get(index)
                ruta_listbox.delete(index)
                ruta_listbox.insert(index - 1, valor)
                ruta_listbox.select_set(index - 1)
            except Exception as e:
                logging.error(f"Error al mover hacia arriba: {e}")

        def mover_abajo():
            try:
                seleccion = ruta_listbox.curselection()
                if not seleccion or seleccion[0] == ruta_listbox.size() - 1:
                    return
                index = seleccion[0]
                valor = ruta_listbox.get(index)
                ruta_listbox.delete(index)
                ruta_listbox.insert(index + 1, valor)
                ruta_listbox.select_set(index + 1)
            except Exception as e:
                logging.error(f"Error al mover hacia abajo: {e}")

        # Botones para mover selección
        btn_arriba = Button(self.ventana_configuracion_ruta, text="↑ Mover Arriba", command=mover_arriba)
        btn_arriba.pack(pady=5)
        btn_abajo = Button(self.ventana_configuracion_ruta, text="↓ Mover Abajo", command=mover_abajo)
        btn_abajo.pack(pady=5)

        # Guardar configuración
        def guardar_configuracion():
            # Obtener el orden personalizado de la ruta de guardado
            ruta_guardado = "/".join(abreviaciones_ruta[ruta_listbox.get(i)] for i in range(ruta_listbox.size()))
            # Cambiar solo la configuración 'ruta_guardado'
            guardar_configuracion_ini('ruta_guardado', ruta_guardado)
            # Cierra luego de guardar
            self.ventana_configuracion_ruta.destroy()

        # Botón para guardar la configuración
        Button(self.ventana_configuracion_ruta, text="Guardar Opción Ruta", command=guardar_configuracion).pack(pady=20)

    def ordenar_documentos_recibidos(self):
        """
        Muestra un mensaje de progreso mientras se ordenan los documentos y retroalimenta el progreso.
        """
        try:
            # Pedir directorio y organizar archivos
            directorio = filedialog.askdirectory(title="Seleccione la Carpeta de Documentos a Ordenar")
            if directorio:
                # Obtener configuraciones necesarias
                nombre_archivo = self.configuraciones.get("nombre_archivo")
                ruta_guardado = self.configuraciones.get("ruta_guardado")
                ruc_actual = self.configuraciones.get("ruc_actual")
                try:
                    # Ordenar documentos y obtener mensajes de progreso
                    resultado = ordenar_documentos(nombre_archivo, ruta_guardado, ruc_actual, "recibidos", directorio)
                    # Formatear los mensajes de éxito y errores
                    organizados = "\n".join(resultado["resultado_organizacion"])
                    eliminados = "\n".join(resultado["resultado_eliminados"])
                    errores = "\n".join(resultado["mensaje_error"]) if resultado["mensaje_error"] else "No hay errores."

                    # Mostrar mensaje de finalización en un messagebox
                    messagebox.showinfo(
                        "Proceso Completado",
                        f"Archivos organizados:\n{organizados}\n\nArchivos eliminados:\n{eliminados}\n\nMensajes de Error:\n{errores}")

                except Exception as e:
                    logging.exception(f"Error durante el ordenamiento de documentos: {e}")
            else:
                messagebox.showinfo("Información", f"No se selecciono ninguna carpeta.")
        except Exception as e:
            logging.exception(f"Error al iniciar la ventana de progreso: {e}")

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
            "Sistema de Gestión de Documentos de SRI\n"
            "Versión: 1.0\n"
            "Desarrollado por: BenderClon\n"
            "Fecha de Desarrollo: Noviembre 2024\n"
            "Tecnologías Utilizadas:\n"
            "- CHATGPT\n"
            "- 6 Michis conmigo\n"
            "- Un incredulo idiota."
        )
        messagebox.showinfo("Acerca de", detalles)
        logging.info("Información 'Acerca de' mostrada.")

    def run(self):
        """
        Ejecuta el bucle principal de la interfaz gráfica.
        """
        self.root.mainloop()
