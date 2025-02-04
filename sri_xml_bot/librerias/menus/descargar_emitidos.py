import os
import logging
import subprocess
import re
import time
import pandas as pd
from tkinter import messagebox, Toplevel
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, NoSuchWindowException, \
    StaleElementReferenceException, NoSuchElementException
from sri_xml_bot.librerias.utils import ruta_relativa_recurso, separar_tipo_y_serie

# WebDriver global para controlarlo en distintas funciones
driver = None
delay_web = 1

def descargar_emitidos(ruta_chromedriver, fecha_emision, estado_autorizacion, tipo_comprobante, estab, pemi, ruc, clave):
    """
    Lógica para descargar documentos emitidos basada en los parámetros seleccionados.

    Args:
        ruta_chromedriver (str): Ruta al ejecutable de ChromeDriver.
        fecha_emision (str): Fecha de emisión en formato "dd/mm/yyyy".
        estado_autorizacion (str): Estado de autorización (ej. AUT-NAT-PPR / Autorizados-No Autorizados-Por Procesar).
        tipo_comprobante (str): Tipo de comprobante (valores "0" a "6").
        estab (str): Establecimiento (ej. "Todos" o el número del establecimiento).
        pemi (str): Punto de emisión.
        ruc (str): RUC procesado.
        clave (str): Clave del RUC.
    """
    try:
        logging.debug("Iniciando descarga de documentos emitidos.")
        logging.info(f"Parámetros de descarga -> Fecha: {fecha_emision}, Estado: {estado_autorizacion}, "
                     f"Tipo: {tipo_comprobante}, Establecimiento: {estab}, Punto de Emisión: {pemi}")

        if not driver:
            configurar_webdriver(ruta_chromedriver)

        iniciar_sesion(ruc, clave)
        seleccionar_opciones_de_consulta(fecha_emision, estado_autorizacion, tipo_comprobante, estab, pemi)
        hay_respuesta = click_consulta()

        if hay_respuesta:
            while True:
                """registros_a_descargar = comparar_registros_emitidos(ruc, fecha_emision)
                filas_procesadas = descargar_comprobantes_emitidos(registros_a_descargar)
                actualizar_excel_emitidos(ruc, filas_procesadas)"""
                if not navegar_a_la_pagina_siguiente():
                    break
            messagebox.showinfo("Descarga completada", "Revisa la carpeta de descargas y organiza los documentos.")
        else:
            messagebox.showinfo("Proceso completado", "No se encontraron registros para descargar o el captcha falló.")

    except NoSuchWindowException:
        logging.error("No se encontró la ventana del navegador: ChromeDriver cerrado inesperadamente.")
        messagebox.showerror("Error", "El navegador ChromeDriver se cerró inesperadamente.")
        liberar_recursos()

    except Exception as e:
        logging.exception("Error durante la descarga de documentos emitidos.")
        messagebox.showerror("Error en la descarga", f"Se produjo un error al descargar los documentos: {e}")
        liberar_recursos()


# ===================================
# Configuración del WebDriver
# ===================================

def configurar_webdriver(ruta):
    """
    Configura el WebDriver de Chrome con las preferencias necesarias para descargar documentos.
    """
    try:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.prompt_for_download": "False",
            "safebrowsing.enabled": "False",
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        ruta_chromedriver = ruta_relativa_recurso(ruta, filetypes=[("Archivos ejecutables", "*.exe")])

        service = Service(executable_path=ruta_chromedriver)
        service.creationflags = subprocess.CREATE_NO_WINDOW  # Oculta la ventana cmd
        global driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver configurado exitosamente.")
    except SessionNotCreatedException:
        logging.error("Error: La versión de ChromeDriver no es compatible con la versión de Chrome instalada.")
        messagebox.showerror("Error",
                             "Descarga la última versión de ChromeDriver y colócala en la carpeta de archivos.")
        liberar_recursos()
    except Exception as e:
        logging.error(f"Error al configurar el WebDriver: {e}")
        messagebox.showerror("Error", f"Error al configurar el WebDriver: {e}")
        liberar_recursos()


# ===================================
# Funciones de Navegación y Acciones en la Web
# ===================================

def iniciar_sesion(usuario, password):
    """
    Inicia sesión en el portal del SRI.
    """
    global driver
    try:
        driver.get("https://srienlinea.sri.gob.ec/sri-en-linea/contribuyente/perfil")
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "usuario"))).send_keys(usuario)
        driver.find_element(By.ID, "password").send_keys(password)
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.ID, "kc-login"))).click()
        logging.info("Inicio de sesión completado.")
    except TimeoutException:
        logging.error("Timeout al intentar iniciar sesión.")
        messagebox.showerror("Error", "No se pudo iniciar sesión. Verifica tu conexión o tus credenciales.")
        liberar_recursos()


def seleccionar_opciones_de_consulta(fecha_emision, estado_autorizacion, tipo_comprobante, estab, pemi):
    """
    Selecciona las opciones de consulta en el portal del SRI.
    """
    global driver
    try:
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Perfil')]")))
        time.sleep(1)
        driver.get("https://srienlinea.sri.gob.ec/tuportal-internet/accederAplicacion.jspa?redireccion=60&idGrupo=58")

        # Esperar a que el enlace de "Comprobantes electrónicos emitidos" esté visible
        enlace_emitidos = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Comprobantes electrónicos emitidos')]")))
        # Ejecutar el JavaScript de la acción de "onclick" del enlace
        driver.execute_script(enlace_emitidos.get_attribute("onclick"))

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:txtParametro"))
        )

        # Ingresar la fecha de emisión
        fecha_emision_input = driver.find_element(By.ID, "frmPrincipal:calendarFechaDesde_input")
        fecha_emision_input.clear()

        # Evitar seleccionar una fecha futura
        fecha_emision_date = datetime.strptime(fecha_emision, "%d/%m/%Y")
        if fecha_emision_date > datetime.now():
            raise ValueError("La fecha de emisión no puede ser en el futuro")

        fecha_emision_input.send_keys(fecha_emision)

        # Seleccionar estado de autorización
        estado_dropdown = Select(driver.find_element(By.ID, "frmPrincipal:cmbEstadoAutorizacion"))
        estado_dropdown.select_by_value(estado_autorizacion)

        # Seleccionar tipo de comprobante
        comprobante_dropdown = Select(driver.find_element(By.ID, "frmPrincipal:cmbTipoComprobante"))
        comprobante_dropdown.select_by_value(tipo_comprobante)

        # Seleccionar establecimiento
        estab_dropdown = Select(driver.find_element(By.ID, "frmPrincipal:cmbEstablecimiento"))
        if estab == "Todos":
            estab_dropdown.select_by_visible_text("Todos")
        else:
            estab_dropdown.select_by_value(estab)

        # Ingresar el punto de emisión
        pemi_input = driver.find_element(By.ID, "frmPrincipal:txtPuntoEmision")
        pemi_input.clear()
        pemi_input.send_keys(pemi)

        logging.info("Opciones de consulta seleccionadas.")
    except TimeoutException:
        logging.error("Timeout al seleccionar opciones de consulta.")
        liberar_recursos()


def click_consulta():
    """
    Realiza la consulta en el portal del SRI después de seleccionar las opciones de búsqueda.
    """
    global driver
    try:
        # Intentar hacer clic en el botón de consulta
        driver.find_element(By.ID, 'btnRecaptcha').click()
        logging.info("Botón de consulta presionado, verificando resultados.")

        # Intentar encontrar el mensaje inmediatamente sin espera
        try:
            mensaje_no_datos = driver.find_element(By.CSS_SELECTOR, "#formMessages\\:messages .ui-messages-warn-summary")
            if "No existen datos para los parámetros ingresados" in mensaje_no_datos.text:
                logging.info("No existen datos para los parámetros ingresados. Retornando lista vacía.")
                liberar_recursos()
                return False
        except (NoSuchElementException, StaleElementReferenceException):
            # Si el mensaje no se encuentra inmediatamente, pasar a buscar la tabla de resultados
            logging.info("Mensaje de 'No existen datos' no encontrado inmediatamente, buscando tabla de resultados.")

        # Esperar la aparición de la tabla de resultados
        try:
            WebDriverWait(driver, 240).until(
                EC.presence_of_element_located((By.ID, "frmPrincipal:tablaCompRecibidos_data"))
            )
            logging.info("Consulta completada, tabla de resultados encontrada.")
            return True
        except TimeoutException:
            logging.error("No se encontró la tabla de resultados después de esperar.")
            liberar_recursos()
            return False

    except TimeoutException:
        logging.error("No se encontró el botón de consulta. Saliendo.")
        liberar_recursos()
        return False


def navegar_a_la_pagina_siguiente():
    """
    Intenta navegar a la página siguiente de resultados.
    Retorna True si el clic en el botón Siguiente fue posible, False si el botón estaba deshabilitado.
    """
    global driver
    # Delay para asegurarse que se ejecuten ciertas acciones.
    time.sleep(delay_web)
    try:
        # Extraer el texto que indica la página actual y el total de páginas
        paginacion_texto = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-paginator-current"))).text

        # Extraer números del texto, se espera un formato como "(1 of 4)"
        match = re.search(r"\((\d+) of (\d+)\)", paginacion_texto)
        if match:
            pagina_actual = int(match.group(1))
            total_paginas = int(match.group(2))

            # Verificar si estamos en la última página
            if pagina_actual >= total_paginas:
                liberar_recursos()
                return False

        # Intentar hacer clic en el botón "Siguiente"
        next_button = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)")))
        next_button.click()
        return True

    except TimeoutException:
        logging.error("No se pudo hacer clic en el botón 'Siguiente'.")
        return False


# ===================================
# Funciones de Procesamiento de Datos
# ===================================
def descargar_comprobantes(tipo_descarga, filas_a_procesar):
    global driver
    # Delay para asegurarse que se ejecuten ciertas acciones.
    time.sleep(delay_web)
    filas_actualizadas = []
    max_documentos = 75  # Máximo de documentos a procesar
    documentos_procesados = 0

    def intentar_descargar(driver, link_id):
        """Función auxiliar para intentar descargar un documento."""
        try:
            driver.execute_script(
                f"mojarra.jsfcljs(document.getElementById('frmPrincipal'),{{'{link_id}':'{link_id}'}},'');return false")
            return True
        except Exception as e:
            logging.error(f"Error al intentar descargar con link_id {link_id}: {e}")
            messagebox.showerror("Error", f"Error al intentar descargar con link_id {link_id}: {e}")
            return False

    for fila in filas_a_procesar:
        if documentos_procesados > max_documentos:
            logging.info(f"Se alcanzó el máximo de {max_documentos} documentos procesados, se avanza hasta la siguiente pagina.")
            navegar_a_la_pagina_siguiente(driver)
            break

        nro = fila[2]
        logging.info(f"Procesando documento: #{nro}")
        intentos = 0
        procesado = False

        while intentos < 3 and not procesado:
            intentos += 1
            if tipo_descarga in ("1", "0"):
                link_xml_id = f"frmPrincipal:tablaCompRecibidos:{int(nro) - 1}:lnkXml"
                procesado = intentar_descargar(driver, link_xml_id)

            if tipo_descarga in ("2", "0") and procesado:
                link_pdf_id = f"frmPrincipal:tablaCompRecibidos:{int(nro) - 1}:lnkPdf"
                procesado = intentar_descargar(driver, link_pdf_id)

            if procesado:
                logging.info(f"Documento #{nro} procesado con éxito.")
                break  # Salir del bucle si se procesó correctamente

            if not procesado:
                logging.info(f"Intento {intentos} fallido para el documento: #{nro}. Reintentando en 2 segundos...")
                time.sleep(2)

        estado = "Procesada" if procesado else "Fallida"
        fila_actualizada = fila + (estado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        filas_actualizadas.append(fila_actualizada)
        if procesado:
            documentos_procesados += 1
        else:
            logging.error(f"No se pudo procesar el documento: #{nro} después de 3 intentos.")
    return filas_actualizadas


def obtener_filas_a_procesar_web():
    """
    Obtiene las filas a procesar desde la tabla de resultados del portal SRI.
    """
    global driver
    # Delay para asegurarse que se ejecuten ciertas acciones.
    time.sleep(delay_web)
    filas_a_procesar = []
    try:
        tabla = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "frmPrincipal:tablaCompRecibidos_data")))
        # Esperar hasta que las filas <tr> estén presentes en el tbody
        filas = WebDriverWait(tabla, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
        for fila in filas:
            celdas = WebDriverWait(fila, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
            if len(celdas) < 6:
                continue
            try:
                nro = int(celdas[0].text.strip())
                ruc = celdas[1].text.strip().split("\n")[0]
                tipo_documento, serie_comprobante = separar_tipo_y_serie(celdas[2].text.strip())
                fecha = celdas[5].text.strip().split("/")
                anio = int(fecha[2])
                mes = int(fecha[1])
                fila_datos = (anio, mes, nro, ruc, tipo_documento, serie_comprobante)
                filas_a_procesar.append(fila_datos)
            except (ValueError, IndexError) as e:
                messagebox.showerror("Error al procesar fila", f"Error en fila: {e}")
        logging.info(f"Se encontraron {len(filas_a_procesar)} filas para procesar.")
    except TimeoutException:
        logging.error("No se pudo cargar la tabla de resultados.")
    except StaleElementReferenceException:
        logging.warning("Elemento obsoleto encontrado en la fila, omitiendo esta fila.")
    return filas_a_procesar


def obtener_filas_a_procesar_excel(ruc, anio=None, mes=None):
    archivo_excel = f"librerias/archivos/docs_{ruc}_2024.xlsx"
    filas_existentes = []

    if os.path.exists(archivo_excel):
        df_existente = pd.read_excel(archivo_excel, dtype=str)
        if anio and mes:
            df_existente_filtro = df_existente[(df_existente['Año'] == str(anio)) & (df_existente['Mes'] == str(mes))]
        else:
            df_existente_filtro = df_existente

        for row in df_existente_filtro.itertuples(index=False):
            fila_datos = (int(row.Año), int(row.Mes), int(row.Nro), row.RUC, row.TipoDocumento, row.SerieComprobante)
            filas_existentes.append(fila_datos)
    return filas_existentes


def obtener_filas_modificadas(filas, ignorar_indice):
    """Transforma cada fila para ignorar el elemento en el índice especificado."""
    return {tuple(fila[i] for i in range(len(fila)) if i != ignorar_indice) for fila in filas}


def recuperar_registros_completos(registros_completos, registros_modificados, ignorar_indice):
    """Recupera los registros completos a partir de los registros modificados."""
    registros_modificados_set = set(registros_modificados)
    return {registro for registro in registros_completos if tuple(registro[i] for i in range(len(registro)) if i != ignorar_indice) in registros_modificados_set}


def comparar_registros(ruc, anio=None, mes=None):
    # Obtener registros desde la web y el archivo Excel
    registros_web = obtener_filas_a_procesar_web()
    registros_excel = obtener_filas_a_procesar_excel(ruc, anio, mes)

    # Transformar los registros para ignorar el tercer elemento (índice 2)
    registros_web_modificados = obtener_filas_modificadas(registros_web, 2)
    registros_excel_modificados = obtener_filas_modificadas(registros_excel, 2)

    # Encontrar registros únicos en la web que no están en el Excel
    solo_en_web_modificados = registros_web_modificados - registros_excel_modificados

    # Recuperar los registros completos a partir de los registros modificados
    solo_en_web = recuperar_registros_completos(registros_web, solo_en_web_modificados, 2)

    return solo_en_web


def actualizar_excel(ruc, procesados=None):
    archivo_excel = f"librerias/archivos/docs_{ruc}_2024.xlsx"

    try:
        if procesados:
            df_nuevas = pd.DataFrame(procesados, columns=["Año", "Mes", "Nro", "RUC", "TipoDocumento", "SerieComprobante", "Estado", "FechaHoraProcesado"])

            if os.path.exists(archivo_excel):
                # Cargar el archivo existente
                df_existente = pd.read_excel(archivo_excel, dtype=str)
                # Añadir nuevas filas al final del DataFrame existente
                df_final = pd.concat([df_existente, df_nuevas], ignore_index=True)
            else:
                # Si no existe el archivo, crear un DataFrame con las nuevas filas
                df_final = df_nuevas

            # Convertir las columnas "Año", "Mes" y "Nro" a enteros antes de guardar
            df_final["Año"] = df_final["Año"].astype(int)
            df_final["Mes"] = df_final["Mes"].astype(int)
            df_final["Nro"] = df_final["Nro"].astype(int)
            df_final.to_excel(archivo_excel, index=False, engine='openpyxl')

    except Exception as e:
        logging.error(f"Se produjo un error al actualizar el archivo Excel: {e}.")
        messagebox.showerror("Error al actualizar el archivo Excel", f"Se produjo un error al actualizar el archivo Excel: {e}")


def liberar_recursos():
    """
    Libera el WebDriver y cierra la sesión de manera segura.
    """
    global driver
    if driver:
        driver.quit()
        logging.info("WebDriver cerrado y recursos liberados.")
    driver = None