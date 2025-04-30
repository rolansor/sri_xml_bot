import tkinter as tk
import os
import sys
import base64
import logging

from tkinter import messagebox, Toplevel, Listbox, Button, simpledialog, Entry, StringVar, OptionMenu, filedialog, Label
from tkinter.constants import END
from PIL import Image, ImageTk
from datetime import datetime

from sri_xml_bot.librerias.encriptar import encriptar_texto, desencriptar_texto
from sri_xml_bot.librerias.menus.generar_pdfs import generar_archivos_pdfs
from sri_xml_bot.librerias.menus.generar_reporte import generar_reporte_xlxs
from sri_xml_bot.librerias.menus.imprimir_pdfs import imprimir_pdfs
from sri_xml_bot.librerias.menus.ordenar_documentos import ordenar_documentos, desclasificar_xmls
from sri_xml_bot.librerias.menus.descargar_documentos import descargar_documentos
from sri_xml_bot.librerias.utils import centrar_ventana, ruta_relativa_recurso, guardar_configuracion_ini, \
    cargar_configuracion_ini


class Application:
    def __init__(self):
        """
        Inicializa la aplicación y configura la ventana principal.
        """
        self.root = tk.Tk()
        self.root.withdraw()

        # Cargar todas las configuraciones al inicio
        self.configuraciones = cargar_configuracion_ini()
        self.master_password = None

        # Si es la primera vez (por ejemplo, no hay clave encriptada), mostramos la configuración inicial
        if not self.configuraciones.get('clave_ruc_encriptada'):
            self.mostrar_configurar_ruc(primer_uso=True)
            # Esperar a que se cierre la ventana de configuración
            self.root.wait_window(self.ventana_config)
            # Volver a cargar la configuración
            self.configuraciones = cargar_configuracion_ini()
            # Si aún no se completó la configuración, mostrar un error y salir
            if not self.configuraciones.get('clave_ruc_encriptada'):
                messagebox.showerror("Error", "Configuración inicial no completada. La aplicación se cerrará.")
                self.root.destroy()
                sys.exit(1)

        # Una vez completada la configuración, se muestra la ventana principal
        self.root.deiconify()  # Muestra la ventana principal
        centrar_ventana("Sistema de Gestión de Documentos", self.root, ancho=800, alto=500)

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

    def pedir_contrasena_maestra(self):
        """
        Solicita una única vez la contraseña maestra y la guarda en memoria.
        """
        master = simpledialog.askstring(
            "Contraseña Maestra",
            "Ingrese su contraseña maestra para desbloquear la aplicación:",
            show="*",
            parent=self.root
        )
        return master

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

        # Submenú de "Clasificar"
        menu_clasificar = tk.Menu(menubar, tearoff=0)
        menu_clasificar.add_command(label="Ordenar Documentos Recibidos",
                                    command=lambda: self.ordenar_documentos("recibidos", False))
        menu_clasificar.add_command(label="Ordenar Documentos Emitidos",
                                    command=lambda: self.ordenar_documentos("emitidos", False))
        menu_clasificar.add_command(label="Reorganizar Documentos Recibidos",
                                    command=lambda: self.ordenar_documentos("recibidos", True))
        menu_clasificar.add_command(label="Reorganizar Documentos Emitidos",
                                    command=lambda: self.ordenar_documentos("emitidos", True))
        menu_clasificar.add_command(label="Extraer XML's", command=self.extraer_xmls)
        menubar.add_cascade(label="Clasificar", menu=menu_clasificar)

        # Submenú de "Reportes"
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menu_reportes.add_command(label="Generar XLS", command=self.generar_reporte)
        menubar.add_cascade(label="Reportes", menu=menu_reportes)

        # Submenú de "PDFs"
        menu_pdfs = tk.Menu(menubar, tearoff=0)
        menu_pdfs.add_command(label="Generar PDFs", command=self.generar_pdfs)
        menu_pdfs.add_command(label="Configurar PDFs", command=self.generar_pdfs)
        menubar.add_cascade(label="PDFs", menu=menu_pdfs)

        # Menú "Configuraciones"
        menu_configuracion = tk.Menu(menubar, tearoff=0)
        menu_configuracion.add_command(label="Ruc/Razon Social/Clave", command=self.mostrar_configurar_ruc)
        menu_configuracion.add_command(label="Estructura de Rutas", command=self.configurar_ruta_guardado)
        menu_configuracion.add_command(label="Formato Nombre Archivo", command=self.configurar_nombre_guardado)
        menu_configuracion.add_command(label="Ruta WebDriver", command=self.configurar_ruta_chromedriver)
        menu_configuracion.add_command(label="Ruta Log", command=self.configurar_ruta_log)
        menu_configuracion.add_command(label="Ruta Logo por defecto", command=self.configurar_ruta_logo)
        menubar.add_cascade(label="Configuraciones", menu=menu_configuracion)


        # Menú "Acerca de"
        menu_acerca_de = tk.Menu(menubar, tearoff=0)
        menu_acerca_de.add_command(label="Detalles del Desarrollo", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Acerca de", menu=menu_acerca_de)

        self.root.config(menu=menubar)

    def descargar_recibidos(self, tipo_documento):
        """
        Utiliza los datos de configuración (RUC y clave) para iniciar el proceso
        de descarga de documentos.
        """
        self.configuraciones = cargar_configuracion_ini()
        # Obtener el RUC configurado
        ruc = self.configuraciones.get('ruc_actual')
        razon_social = self.configuraciones.get('razon_social')
        if not ruc:
            messagebox.showerror("Error", "No se configuró el RUC en las configuraciones.", parent=self.root)
            return

        # Obtener la clave encriptada y la sal de la configuración
        clave_encriptada = self.configuraciones.get('clave_ruc_encriptada')
        salt_str = self.configuraciones.get('clave_salt')
        if not clave_encriptada or not salt_str:
            messagebox.showerror("Error", "No se configuró la clave en las configuraciones.", parent=self.root)
            return

        # Pedir contraseña maestra solo la primera vez
        if not self.master_password:
            self.master_password = simpledialog.askstring(
                "Contraseña Maestra", "Ingrese la contraseña maestra:",
                show="*", parent=self.root)
            if not self.master_password:
                messagebox.showwarning("Cancelado",
                                       "No se ingresó la contraseña maestra.",
                                       parent=self.root)
                return
        try:
            # Convertir la sal (almacenada en base64) a bytes
            salt = base64.urlsafe_b64decode(salt_str.encode())
        except Exception as e:
            messagebox.showerror("Error", f"Error al decodificar la sal: {e}", parent=self.root)
            logging.exception("Error al decodificar la sal.")
            return

        try:
            # Desencriptar la clave usando la contraseña maestra y la sal
            clave = desencriptar_texto(clave_encriptada, self.master_password, salt)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo desencriptar la clave: {e}", parent=self.root)
            logging.exception("Error al desencriptar la clave.")
            return

        # Con la información obtenida (razón social, RUC y clave), continuamos directamente
        datos = (razon_social, ruc, clave)
        self.mostrar_opciones(datos, tipo_documento)

    def mostrar_opciones(self, datos, tipo_documento):

        # Extraer los datos del cliente
        nombre, ruc, clave = datos

        ventana_opciones = Toplevel(self.root)
        centrar_ventana(f"Opciones de Descarga para {nombre}", ventana_opciones, ancho=400, alto=400)
        ventana_opciones.grab_set()  # Bloquear interacción con la ventana de selección hasta que se cierre
        ventana_opciones.transient(self.root)

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

    def ordenar_documentos(self, emitido_recibido, recursivo):
        """
        Muestra un mensaje de progreso mientras se ordenan los documentos y retroalimenta el progreso.
        """
        self.configuraciones = cargar_configuracion_ini()
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
                    resultado = ordenar_documentos(nombre_archivo, ruta_guardado, ruc_actual, emitido_recibido,
                                                   directorio, recursivo)
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

    def extraer_xmls(self):
        """
        Muestra un mensaje de progreso mientras se ordenan los documentos y retroalimenta el progreso.
        """
        self.configuraciones = cargar_configuracion_ini()
        try:
            # Pedir directorio y organizar archivos
            directorio = filedialog.askdirectory(title="Seleccione la carpeta de documentos a extraer los xmls")
            if directorio:
                try:
                    # Ordenar documentos y obtener mensajes de progreso
                    resultado = desclasificar_xmls(directorio)
                    messagebox.showinfo(
                        "Proceso Completado",
                        f"Archivos organizados:\n{resultado}")

                except Exception as e:
                    logging.exception(f"Error durante la extracción de XMLs: {e}")
            else:
                messagebox.showinfo("Información", f"No se selecciono ninguna carpeta.")
        except Exception as e:
            logging.exception(f"Error al iniciar la ventana de progreso: {e}")

    def generar_reporte(self):
        """
        Maneja la opción de generar reportes.
        """
        self.configuraciones = cargar_configuracion_ini()
        try:
            # Pedir directorio y organizar archivos
            directorio = filedialog.askdirectory(title="Seleccione la carpeta raiz, desde donde se procesaran los documentos.")
            if directorio:
                try:
                    # Ordenar documentos y obtener mensajes de progreso
                    generar_reporte_xlxs(self.root, directorio)
                except Exception as e:
                    logging.exception(f"Error durante la generación del reporte Excel: {e}")
            else:
                messagebox.showinfo("Información", f"No se selecciono ninguna carpeta raiz.")
        except Exception as e:
            logging.exception(f"Error al iniciar la ventana de progreso: {e}")

    def generar_pdfs(self):
        """
        Maneja la opción de generar PDFs.
        """
        self.configuraciones = cargar_configuracion_ini()
        try:
            # Pedir directorio y organizar archivos
            directorio = filedialog.askdirectory(
                title="Seleccione la carpeta raiz, desde donde se procesaran los xmls.")
            if directorio:
                try:
                    # Ordenar documentos y obtener mensajes de progreso
                    generar_archivos_pdfs(self.root, directorio)
                except Exception as e:
                    logging.exception(f"Error durante la generación de los PDFs: {e}")
            else:
                messagebox.showinfo("Información", f"No se selecciono ninguna carpeta raiz.")
        except Exception as e:
            logging.exception(f"Error al iniciar la ventana de progreso: {e}")

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

    def mostrar_configurar_ruc(self, primer_uso=False):
        """
        Muestra una ventana para configurar o actualizar el RUC, la Razón Social, la clave y la contraseña maestra.
        Si es primer_uso=True, actúa como configuración inicial obligatoria.
        """
        # TODO: El nuevo RUC no se actualiza dinamicamente, toca cerrar todo o volver a cargar.

        self.ventana_config = Toplevel(self.root)
        titulo = "Configuración Inicial" if primer_uso else "Actualizar RUC / Razón Social / Clave"
        self.ventana_config.title(titulo)
        centrar_ventana(titulo, self.ventana_config, ancho=400, alto=300)
        self.ventana_config.grab_set()

        Label(self.ventana_config, text="Ingrese el RUC:").pack(pady=5)
        entry_ruc = Entry(self.ventana_config)
        entry_ruc.pack(pady=5)

        Label(self.ventana_config, text="Ingrese la Razón Social:").pack(pady=5)
        entry_razon = Entry(self.ventana_config)
        entry_razon.pack(pady=5)

        Label(self.ventana_config, text="Ingrese la clave:").pack(pady=5)
        entry_clave = Entry(self.ventana_config, show="*")
        entry_clave.pack(pady=5)

        Label(self.ventana_config, text="Contraseña maestra:").pack(pady=5)
        entry_master = Entry(self.ventana_config, show="*")
        entry_master.pack(pady=5)

        def guardar():
            ruc = entry_ruc.get().strip()
            razon_social = entry_razon.get().strip().upper()
            clave = entry_clave.get().strip()
            master = entry_master.get().strip()

            if not (ruc and razon_social and clave and master):
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.ventana_config)
                return

            if not (ruc.isdigit() and len(ruc) == 13):
                messagebox.showerror("Error", "El RUC debe tener exactamente 13 dígitos numéricos.", parent=self.ventana_config)
                return

            if len(razon_social) < 3:
                messagebox.showerror("Error", "La Razón Social debe tener al menos 3 caracteres.", parent=self.ventana_config)
                return

            salt = os.urandom(16)
            clave_encriptada = encriptar_texto(clave, master, salt)
            salt_str = base64.urlsafe_b64encode(salt).decode()

            guardar_configuracion_ini('ruc_actual', ruc)
            guardar_configuracion_ini('razon_social', razon_social)
            guardar_configuracion_ini('clave_ruc_encriptada', clave_encriptada)
            guardar_configuracion_ini('clave_salt', salt_str)

            messagebox.showinfo("Configuración guardada", "La configuración se ha guardado correctamente.", parent=self.ventana_config)
            self.ventana_config.destroy()

            # Si es primer uso y no se configuró, cerrar app
            if primer_uso:
                self.configuraciones = cargar_configuracion_ini()
                if not self.configuraciones.get('clave_ruc_encriptada'):
                    self.root.destroy()
                    sys.exit(1)

        Button(self.ventana_config, text="Aceptar", command=guardar).pack(pady=10)

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

        # Cargar orden de ruta desde la configuración INI
        ruta_guardado_conf = self.configuraciones.get('ruta_guardado', '')
        # Definimos el mapeo entre texto visible y su abreviatura en configuración
        abreviaciones_ruta = {
            "Ruta Base": "RutaBase",
            "RUC": "RUC",
            "Recibido/Emitido": "RecEmi",
            "Año": "Año",
            "Mes": "Mes",
            "PDF/XML": "XML",
            "Tipo Documento": "TipoDocumento"
        }
        # Construir mapeo inverso: abreviatura -> texto visible
        rev_abreviaciones = {abrev: display for display, abrev in abreviaciones_ruta.items()}

        # Intentar derivar el orden de opción desde la configuración
        ruta_opciones = []  # Lista de textos visibles en el orden deseado
        for parte in ruta_guardado_conf.split('/'):
            texto = rev_abreviaciones.get(parte)
            if texto:
                ruta_opciones.append(texto)

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
            "Fecha + Secuencial": "fecha_secuencial",
            "Nombre Truncado + Secuencial": "nombre_secuencial"
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

    def configurar_ruta_chromedriver(self):
        """Ventana para configurar la ruta del ChromeDriver."""
        win = Toplevel(self.root)
        win.title("Configurar Ruta WebDriver")
        centrar_ventana("Configurar Ruta WebDriver", win, ancho=400, alto=150)
        win.grab_set()

        Label(win, text="Ruta actual:").pack(pady=5)
        ruta_actual = self.configuraciones.get('ruta_chromedriver', '')
        entry = Entry(win, width=50)
        entry.insert(0, ruta_actual)
        entry.pack(pady=5)

        def seleccionar_archivo():
            nueva_ruta = filedialog.askopenfilename(
                title="Seleccionar ChromeDriver",
                filetypes=[("Archivos ejecutables", "*.exe")]
            )
            if nueva_ruta:
                entry.delete(0, END)
                entry.insert(0, nueva_ruta)

        Button(win, text="Seleccionar archivo", command=seleccionar_archivo).pack(pady=5)

        def guardar():
            nueva_ruta = entry.get().strip()
            if nueva_ruta:
                guardar_configuracion_ini('ruta_chromedriver', nueva_ruta)
                messagebox.showinfo("Configuración guardada", "La ruta de WebDriver se ha actualizado.", parent=win)
                self.configuraciones['ruta_chromedriver'] = nueva_ruta
                win.destroy()
            else:
                messagebox.showerror("Error", "La ruta no puede estar vacía.", parent=win)

        Button(win, text="Guardar", command=guardar).pack(pady=5)

    def configurar_ruta_log(self):
        """Ventana para configurar la ruta del archivo de log."""
        win = Toplevel(self.root)
        win.title("Configurar Ruta Log")
        centrar_ventana("Configurar Ruta Log", win, ancho=400, alto=150)
        win.grab_set()

        Label(win, text="Ruta actual:").pack(pady=5)
        ruta_actual = self.configuraciones.get('ruta_logs', '')
        entry = Entry(win, width=50)
        entry.insert(0, ruta_actual)
        entry.pack(pady=5)

        def seleccionar_archivo():
            nueva_ruta = filedialog.asksaveasfilename(
                title="Seleccionar o crear archivo Log",
                filetypes=[("Archivos de log", "*.log")],
                defaultextension=".log"
            )
            if nueva_ruta:
                entry.delete(0, END)
                entry.insert(0, nueva_ruta)

        Button(win, text="Seleccionar archivo", command=seleccionar_archivo).pack(pady=5)

        def guardar():
            nueva_ruta = entry.get().strip()
            if nueva_ruta:
                guardar_configuracion_ini('ruta_logs', nueva_ruta)
                messagebox.showinfo("Configuración guardada", "La ruta de Log se ha actualizado.", parent=win)
                self.configuraciones['ruta_logs'] = nueva_ruta
                win.destroy()
            else:
                messagebox.showerror("Error", "La ruta no puede estar vacía.", parent=win)

        Button(win, text="Guardar", command=guardar).pack(pady=5)

    def configurar_ruta_logo(self):
        """Ventana para configurar la ruta del logo por defecto."""
        win = Toplevel(self.root)
        win.title("Configurar Ruta Logo")
        centrar_ventana("Configurar Ruta Logo", win, ancho=400, alto=150)
        win.grab_set()

        Label(win, text="Ruta actual:").pack(pady=5)
        ruta_actual = self.configuraciones.get('ruta_logos', '')
        entry = Entry(win, width=50)
        entry.insert(0, ruta_actual)
        entry.pack(pady=5)

        def seleccionar_archivo():
            nueva_ruta = filedialog.askopenfilename(
                title="Seleccionar imagen del logo",
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if nueva_ruta:
                entry.delete(0, END)
                entry.insert(0, nueva_ruta)

        Button(win, text="Seleccionar archivo", command=seleccionar_archivo).pack(pady=5)

        def guardar():
            nueva_ruta = entry.get().strip()
            if nueva_ruta:
                guardar_configuracion_ini('ruta_logos', nueva_ruta)
                messagebox.showinfo("Configuración guardada", "La ruta del logo se ha actualizado.", parent=win)
                self.configuraciones['ruta_logos'] = nueva_ruta
                win.destroy()
            else:
                messagebox.showerror("Error", "La ruta no puede estar vacía.", parent=win)

        Button(win, text="Guardar", command=guardar).pack(pady=5)

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
