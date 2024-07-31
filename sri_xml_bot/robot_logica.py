import os
import re
import logging
import pandas as pd
import tkinter as tk
import time
import atexit
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, SessionNotCreatedException
from datetime import datetime
from librerias.auxiliares import mostrar_mensaje, centrar_ventana, ruta_relativa_recurso

# Configuración del logging
logging.basicConfig(filename='sri_robot.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

driver = None  # Definir el driver a nivel global para acceder a él en todas las funciones


# Función para liberar recursos
def liberar_recursos():
    global driver
    if driver:
        driver.quit()
        logging.info("WebDriver cerrado y recursos liberados.")


# Registrar la función para ejecutar al finalizar el script
atexit.register(liberar_recursos)


def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Entrando a la función: {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Saliendo de la función: {func.__name__}. Tiempo de ejecución: {end_time - start_time:.2f} segundos")
        return result
    return wrapper


def manejar_excepcion(func):
    def wrapper(*args, **kwargs):
        driver = args[0]
        try:
            return func(*args, **kwargs)
        except TimeoutException:
            verificar_y_recargar(driver)
            return func(*args, **kwargs)
        except NoSuchWindowException:
            logging.error("No se encontró la ventana del navegador: ChromeDriver cerrado inesperadamente.")
            mostrar_mensaje("Error", "El navegador ChromeDriver se cerró inesperadamente.")
            liberar_recursos()
            exit(1)
        except FileNotFoundError as e:
            logging.error(f"No se encontró el archivo: {e}")
            mostrar_mensaje("Error", f"No se encontró el archivo: {e}")
            liberar_recursos()
            exit(1)
        except Exception as e:
            logging.error(f"Excepción no manejada: {e}")
            mostrar_mensaje("Error", f"Excepción no manejada: {e}")
            liberar_recursos()
            exit(1)
    return wrapper


def separar_tipo_y_serie(comprobante):
    # Define una expresión regular para separar el tipo y la serie de comprobante
    match = re.match(r"(.+?)\s+(\d{3}-\d{3}-\d{9})", comprobante)
    if match:
        tipo = match.group(1).strip()
        serie = match.group(2).strip()
        return tipo, serie
    else:
        return None, None


@manejar_excepcion
@medir_tiempo
def verificar_y_recargar(driver):
    """
    Verifica si la página contiene el mensaje específico y recarga la página después de 5 segundos.
    """
    intentos = 0
    while intentos < 5:
        try:
            body_style = driver.find_element(By.CSS_SELECTOR, "body").get_attribute("style")
            if "background" in body_style and "sri_mant_pro.jpg" in body_style:
                mostrar_mensaje("Página de mantenimiento detectada", "Se detectó la página de mantenimiento. Esperando 5 segundos para recargar la página.")
                time.sleep(5)
                driver.refresh()
                mostrar_mensaje("Página recargada", "La página se ha recargado con éxito.")
                return 1
            else:
                mostrar_mensaje("Excepción Lanzada", "Se detectó una falta de acceso. Esperando 5 segundos para recargar la página.")
                time.sleep(5)
                driver.refresh()
                mostrar_mensaje("Página recargada", "La página se ha recargado con éxito.")
                return 0
        except Exception as e:
            logging.error(f"Error al verificar el fondo de la página: {e}")
            intentos += 1
            if intentos >= 5:
                mostrar_mensaje("Error", "No se pudo recargar la página después de 5 intentos.")
                return 0
            time.sleep(5)
    return 0


# Configura el WebDriver de Chrome
@medir_tiempo
def configurar_webdriver():
    try:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.prompt_for_download": "False",
            "safebrowsing.enabled": "False",
            "profile.default_content_setting_values.automatic_downloads": 1  # Permite múltiples descargas
        }
        chrome_options.add_experimental_option("prefs", prefs)
        ruta_chromedriver = ruta_relativa_recurso('archivos_necesarios/chromedriver.exe')
        # Verificación de existencia del archivo
        if not os.path.exists(ruta_chromedriver):
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_chromedriver = os.path.join(directorio_actual, '../archivos_necesarios/chromedriver.exe')

        service = Service(executable_path=ruta_chromedriver)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except SessionNotCreatedException:
        logging.error("La versión de ChromeDriver no es compatible con la versión de Chrome instalada.")
        mostrar_mensaje("Error", "ChromeDriver desactualizado o incompatible con la versión de Chrome instalada.")
        liberar_recursos()
        exit(1)


# Inicia sesión en el sitio web del SRI
@manejar_excepcion
@medir_tiempo
def iniciar_sesion(driver, usuario, contrasena):
    driver.get("https://srienlinea.sri.gob.ec/sri-en-linea/contribuyente/perfil")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "usuario"))).send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(contrasena)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "kc-login"))).click()


# Selecciona las opciones de consulta en el formulario
@manejar_excepcion
@medir_tiempo
def seleccionar_opciones_de_consulta(driver, anio, mes, dia, tipo_comprobante):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Perfil')]")))
    driver.get("https://srienlinea.sri.gob.ec/tuportal-internet/accederAplicacion.jspa?redireccion=57&idGrupo=55")
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "frmPrincipal:txtParametro")))
    Select(driver.find_element(By.ID, 'frmPrincipal:ano')).select_by_visible_text(anio)
    Select(driver.find_element(By.ID, 'frmPrincipal:mes')).select_by_value(mes)
    if dia == '0':
        Select(driver.find_element(By.ID, 'frmPrincipal:dia')).select_by_visible_text("Todos")
    else:
        Select(driver.find_element(By.ID, 'frmPrincipal:dia')).select_by_visible_text(dia)
    Select(driver.find_element(By.ID, 'frmPrincipal:cmbTipoComprobante')).select_by_visible_text(tipo_comprobante)
    time.sleep(2)


@manejar_excepcion
@medir_tiempo
def click_consulta(driver):
    """
    Hace clic en el botón de consulta para iniciar la búsqueda de comprobantes.
    """
    driver.find_element(By.ID, 'btnRecaptcha').click()

    try:
        WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@title, 'reCAPTCHA')]")))
        logging.info("reCAPTCHA aparecio. Resuelvelo para continuar con la consulta...")
    except Exception as e:
        logging.info(f"No se encontró el reCAPTCHA u ocurrió otro problema: {e}")
    finally:
        # Cambia de nuevo al contenido principal
        driver.switch_to.default_content()
        try:
            # Espera hasta que el reCAPTCHA sea resuelto manualmente (máximo 2 minutos)
            # Localiza el desplegable para seleccionar el número de elementos por página
            num_elementos_selector = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-paginator-rpp-options"))
            )
            logging.info("reCAPTCHA resuelto, seguimos con la consulta.")
            # Intenta seleccionar 75
            Select(num_elementos_selector).select_by_value("75")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Error al interactuar con el selector de elementos por página: {e}")

@manejar_excepcion
@medir_tiempo
def navegar_a_la_pagina_siguiente(driver):
    """
    Intenta navegar a la página siguiente de resultados.
    Retorna True si el clic en el botón Siguiente fue posible, False si el botón estaba deshabilitado.
    """
    try:
        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)")))
        next_button.click()
        return True
    except TimeoutException:
        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)")))
            next_button.click()
            return True
        except TimeoutException:
            return False


@manejar_excepcion
@medir_tiempo
def descargar_comprobantes(driver, tipo_descarga, filas_a_procesar):
    filas_actualizadas = []

    for fila in filas_a_procesar:
        nro = fila[2]
        logging.info(f"Procesando documento: #{nro}")
        intentos = 0
        procesado = False

        while intentos < 3 and not procesado:
            try:
                link_xml_id = f"frmPrincipal:tablaCompRecibidos:{int(nro) - 1}:lnkXml"
                link_pdf_id = f"frmPrincipal:tablaCompRecibidos:{int(nro) - 1}:lnkPdf"
                if tipo_descarga in ("XML", "Ambos"):
                    driver.execute_script(
                        f"mojarra.jsfcljs(document.getElementById('frmPrincipal'),{{'{link_xml_id}':'{link_xml_id}'}},'');return false")

                if tipo_descarga in ("PDF", "Ambos"):
                    driver.execute_script(
                        f"mojarra.jsfcljs(document.getElementById('frmPrincipal'),{{'{link_pdf_id}':'{link_pdf_id}'}},'');return false")
                procesado = True
            except Exception:
                # intenta recargar y jode todo
                temp = verificar_y_recargar(driver)
                if temp == 0:
                    logging.info(f"Intento {intentos + 1} fallido para el documento: #{nro}.")
                    intentos += 1

                    if intentos >= 3:
                        logging.error(f"No se pudo procesar el documento: #{nro} después de 3 intentos.")
                        break

                    # Intentar nuevamente la descarga después de un breve retraso
                    time.sleep(2)

        if procesado:
            fila_actualizada = fila + ("Procesada", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            filas_actualizadas.append(fila_actualizada)
            logging.info(f"Documento #{nro} procesado con éxito.")
        else:
            fila_actualizada = fila + ("Fallida", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            filas_actualizadas.append(fila_actualizada)
            logging.error(f"No se pudo procesar el documento: #{nro} después de 3 intentos.")
    return filas_actualizadas


@medir_tiempo
def leer_y_procesar_excel(driver, ruc, anio=None, mes=None, procesados=None):
    archivo_excel = f"docs_{ruc}_2024.xlsx"
    datos_existentes = set()
    df_existente = None

    if os.path.exists(archivo_excel):
        df_existente = pd.read_excel(archivo_excel, dtype=str)
        if anio and mes:
            df_existente = df_existente[(df_existente['Año'] == str(anio)) & (df_existente['Mes'] == str(mes))]
        for row in df_existente.itertuples(index=False):
            datos_existentes.add((int(row.Año), int(row.Mes), int(row.Nro), row.RUC, row.TipoDocumento, row.SerieComprobante, row.Estado, row.FechaHoraProcesado))

    if procesados is None:
        return obtener_filas_a_procesar(driver, datos_existentes)
    else:
        try:
            if procesados:
                df_nuevas = pd.DataFrame(procesados, columns=["Año", "Mes", "Nro", "RUC", "TipoDocumento", "SerieComprobante", "Estado", "FechaHoraProcesado"])
                if df_existente is not None:
                    # Iterar sobre las filas nuevas para actualizar o añadir según corresponda
                    for index, row in df_nuevas.iterrows():
                        condition = (
                            (df_existente['Año'] == str(row['Año'])) &
                            (df_existente['Mes'] == str(row['Mes'])) &
                            (df_existente['Nro'] == str(row['Nro'])) &
                            (df_existente['RUC'] == row['RUC']) &
                            (df_existente['TipoDocumento'] == row['TipoDocumento']) &
                            (df_existente['SerieComprobante'] == row['SerieComprobante'])
                        )

                        if df_existente.loc[condition].empty:
                            # Si no hay coincidencia, añadir la nueva fila
                            df_existente = pd.concat([df_existente, row.to_frame().T], ignore_index=True)
                        else:
                            # Si hay coincidencia, actualizar la fila existente
                            df_existente.loc[condition, ['Estado', 'FechaHoraProcesado']] = row[['Estado', 'FechaHoraProcesado']]

                    df_final = df_existente
                else:
                    df_final = df_nuevas

                # Convertir las columnas "Año", "Mes" y "Nro" a enteros antes de guardar
                df_final["Año"] = df_final["Año"].astype(int)
                df_final["Mes"] = df_final["Mes"].astype(int)
                df_final["Nro"] = df_final["Nro"].astype(int)
                df_final.to_excel(archivo_excel, index=False, engine='openpyxl')

        except Exception as e:
            mostrar_mensaje("Error al actualizar el archivo Excel", f"Se produjo un error al actualizar el archivo Excel: {e}")


@manejar_excepcion
@medir_tiempo
def obtener_filas_a_procesar(driver, datos_existentes):
    filas_a_procesar = []
    tabla = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "frmPrincipal:tablaCompRecibidos_data"))
    )
    filas = tabla.find_elements(By.TAG_NAME, "tr")
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        if len(celdas) < 6:
            continue
        nro = int(celdas[0].text.strip())
        ruc = celdas[1].text.strip().split("\n")[0]
        tipo_documento, serie_comprobante = separar_tipo_y_serie(celdas[2].text.strip())
        anio = int(celdas[5].text.strip().split("/")[2])
        mes = int(celdas[5].text.strip().split("/")[1])
        fila_datos = (anio, mes, nro, ruc, tipo_documento, serie_comprobante)
        if fila_datos not in [(int(row[0]), int(row[1]), int(row[2]), row[3], row[4], row[5]) for row in datos_existentes] or not any((fila_datos == (int(row[0]), int(row[1]), int(row[2]), row[3], row[4], row[5]) and row[6] == "Procesada" and pd.notna(row[7])) for row in datos_existentes):
            filas_a_procesar.append(fila_datos)
    return filas_a_procesar


def pedir_input_centrado(titulo, mensaje, root, show=None):
    input_dialog = tk.Toplevel()
    input_dialog.withdraw()
    input_dialog.title(titulo)
    input_dialog.geometry("200x100")
    input_dialog.attributes("-topmost", True)
    centrar_ventana(input_dialog)
    tk.Label(input_dialog, text=mensaje).pack(pady=10)
    input_var = tk.StringVar()
    input_entry = tk.Entry(input_dialog, textvariable=input_var, show=show)
    input_entry.pack(pady=10)
    input_entry.focus_force()

    def on_submit():
        input_dialog.quit()
        input_dialog.destroy()

    def cerrar_programa():
        input_dialog.quit()
        input_dialog.destroy()
        root.quit()

    input_dialog.protocol("WM_DELETE_WINDOW", cerrar_programa)
    input_dialog.deiconify()
    input_dialog.mainloop()
    return input_var.get()


def pedir_fecha(titulo, root, mensaje, anios, meses, dias):
    fecha = {"anio": None, "mes": None, "dia": None, "tipo_descarga": None}

    def seleccionar_fecha():
        fecha["anio"] = anio_combobox.get()
        fecha["mes"] = mes_combobox.get()
        fecha["dia"] = dia_combobox.get()
        fecha["tipo_descarga"] = tipo_descarga_combobox.get()
        fecha_dialog.quit()
        fecha_dialog.destroy()

    def cerrar_programa():
        fecha_dialog.quit()
        fecha_dialog.destroy()
        root.quit()

    fecha_dialog = tk.Toplevel()
    fecha_dialog.withdraw()
    fecha_dialog.title(titulo)
    fecha_dialog.geometry("300x350")
    fecha_dialog.attributes("-topmost", True)
    centrar_ventana(fecha_dialog)

    tk.Label(fecha_dialog, text=mensaje).pack(pady=10)
    tk.Label(fecha_dialog, text="Año:").pack(pady=5)
    anio_combobox = ttk.Combobox(fecha_dialog, values=list(anios.values()))
    anio_combobox.pack(pady=5)
    anio_combobox.set(datetime.now().year)

    tk.Label(fecha_dialog, text="Mes:").pack(pady=5)
    mes_combobox = ttk.Combobox(fecha_dialog, values=list(meses.values()))
    mes_combobox.pack(pady=5)
    mes_combobox.set(datetime.now().month)

    tk.Label(fecha_dialog, text="Día:").pack(pady=5)
    dia_combobox = ttk.Combobox(fecha_dialog, values=["Todos"] + list(dias.values()))
    dia_combobox.pack(pady=5)
    dia_combobox.current(0)

    tk.Label(fecha_dialog, text="Tipo de descarga:").pack(pady=5)
    tipo_descarga_combobox = ttk.Combobox(fecha_dialog, values=["XML", "PDF", "Ambos"])
    tipo_descarga_combobox.pack(pady=5)
    tipo_descarga_combobox.current(0)

    tk.Button(fecha_dialog, text="Aceptar", command=seleccionar_fecha).pack(pady=10)
    fecha_dialog.protocol("WM_DELETE_WINDOW", cerrar_programa)
    fecha_dialog.deiconify()
    fecha_dialog.mainloop()

    return fecha["anio"], fecha["mes"], fecha["dia"], fecha["tipo_descarga"]


def pedir_opcion_centrada(titulo, root, mensaje, opciones):
    opcion = tk.StringVar()

    def seleccionar_opcion(opcion_seleccionada):
        opcion.set(opcion_seleccionada)
        opcion_dialog.quit()
        opcion_dialog.destroy()

    def cerrar_programa():
        opcion.set("")
        opcion_dialog.quit()
        opcion_dialog.destroy()
        root.quit()

    opcion_dialog = tk.Toplevel()
    opcion_dialog.withdraw()
    opcion_dialog.title(titulo)
    opcion_dialog.geometry("400x300")
    opcion_dialog.attributes("-topmost", True)
    centrar_ventana(opcion_dialog)
    tk.Label(opcion_dialog, text=mensaje).pack(pady=10)
    for texto, valor in opciones.items():
        tk.Button(opcion_dialog, text=texto, command=lambda v=texto: seleccionar_opcion(v)).pack(pady=5)
    opcion_dialog.protocol("WM_DELETE_WINDOW", cerrar_programa)
    opcion_dialog.deiconify()
    opcion_dialog.mainloop()
    return opcion.get()


def cargar_rucs_credenciales_desde_archivo():
    rucs = {}
    ruta_archivo = ruta_relativa_recurso('archivos_necesarios/credenciales_rucs.txt')

    # Verificación de existencia del archivo
    if not os.path.exists(ruta_archivo):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(directorio_actual, '../archivos_necesarios/credenciales_rucs.txt')

    try:
        with open(ruta_archivo, 'r') as archivo:
            for linea in archivo:
                # Eliminar espacios en blanco y saltos de línea
                linea = linea.strip()
                # Ignorar líneas vacías
                if not linea:
                    continue
                # Dividir la línea en partes separadas por comas
                partes = linea.split(',')
                if len(partes) == 3:
                    nombre, ruc, clave = partes
                    rucs[f"{nombre} ({ruc})"] = (ruc, clave)
                else:
                    print(f"Línea malformada: {linea}")
        rucs["Ingresar Manualmente"] = "manual"
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return rucs