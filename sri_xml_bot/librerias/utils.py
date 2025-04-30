import configparser
import os
import sys
from tkinter import Tk, messagebox, filedialog
import re
import logging
import hashlib


def obtener_directorio_base() -> str:
    """
    Retorna el directorio base según el entorno de ejecución (frozen o no).
    """
    return os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)


def centrar_ventana(titulo: str, ventana, ancho: int = 800, alto: int = 500) -> None:
    """
    Centra una ventana en la pantalla con un tamaño fijo.
    """
    ventana.title(titulo)
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.resizable(False, False)


def ruta_relativa_recurso(relativa: str, filetypes=[("Archivos de texto", "*.txt")]) -> str:
    """
    Retorna la ruta correcta de un recurso en el mismo directorio desde el que se ejecuta el .exe.
    Si no se encuentra, abre un diálogo para que el usuario seleccione el archivo manualmente.
    """
    base_dir = obtener_directorio_base()
    ruta_archivo = os.path.join(base_dir, relativa)

    # Verificar si el archivo existe en la ubicación esperada
    while not os.path.exists(ruta_archivo):
        logging.warning(f"Archivo no encontrado: {ruta_archivo}")
        temporal = Tk()
        temporal.withdraw()  # Oculta la ventana principal de Tk
        file_name = os.path.basename(ruta_archivo)

        respuesta = messagebox.askretrycancel(
            "Archivo no encontrado",
            f"No se encontró el archivo {file_name}. ¿Desea intentar seleccionarlo manualmente?"
        )

        if not respuesta:
            messagebox.showinfo("Operación cancelada", "No se seleccionó ningún archivo. Cerrando aplicación.")
            temporal.destroy()
            sys.exit(1)

        ruta_archivo = filedialog.askopenfilename(
            title=f"Seleccione el archivo {file_name}",
            filetypes=filetypes,
            initialdir=base_dir
        )

        if not ruta_archivo:
            messagebox.showwarning("Selección inválida", "No seleccionó ningún archivo. Inténtelo de nuevo o cancele.")
            temporal.destroy()
        else:
            logging.info(f"Archivo seleccionado manualmente: {ruta_archivo}")
            temporal.destroy()
            break

    return ruta_archivo


def separar_tipo_y_serie(comprobante: str) -> tuple:
    """
    Separa el tipo y la serie de un comprobante con el formato:
    "tipo documento 000-000-00000000".
    """
    match = re.match(r"(.+?)\s+(\d{3}-\d{3}-\d{9})", comprobante)
    if not match:
        logging.debug(f"No se pudo separar tipo y serie para: {comprobante}")
        return (None, None)
    return (match.group(1).strip(), match.group(2).strip())


def cargar_configuracion_ini() -> dict:
    """
    Carga las configuraciones desde un archivo .ini y devuelve un diccionario con los valores.
    """
    configuraciones = {
        "nombre_archivo": "ruc_secuencial",
        "ruta_guardado": "RutaBase/RUC/RecEmi/Año/Mes/XML/TipoDocumento",
        "ruc_actual": "9999999999999",
        "razon_social": "S/N",
        "clave_ruc_encriptada": "",
        "clave_salt": "",
        "ruta_chromedriver": "../archivos/chromedriver.exe",
        "ruta_logos": "../archivos/logo.png",
        "ruta_rucs": "../archivos/rucs.txt",
        "ruta_logs": "../archivos/app.log",
    }

    archivo_ini = '../archivos/configuraciones.ini'
    base_dir = obtener_directorio_base()
    ruta_config = os.path.join(base_dir, archivo_ini)

    if os.path.exists(ruta_config):
        config = configparser.ConfigParser()
        try:
            config.read(ruta_config)
            if 'Configuracion' in config:
                for key in configuraciones.keys():
                    configuraciones[key] = config.get("Configuracion", key, fallback=configuraciones[key])
                logging.info(f"Configuración cargada desde {ruta_config}")
            else:
                logging.warning("La sección 'Configuracion' no se encontró en el archivo. Usando valores predeterminados.")
        except configparser.Error as e:
            logging.error(f"Error al leer el archivo de configuración: {e}. Usando valores predeterminados.")
    else:
        logging.warning(f"Archivo de configuración '{archivo_ini}' no encontrado. Usando valores predeterminados.")

    return configuraciones


def guardar_configuracion_ini(config_key: str, config_value: str) -> None:
    """
    Guarda o actualiza una configuración en el archivo .ini.
    """
    archivo_ini = '../archivos/configuraciones.ini'
    base_dir = obtener_directorio_base()
    ruta_config = os.path.join(base_dir, archivo_ini)

    while not os.path.exists(ruta_config):
        temporal = Tk()
        temporal.withdraw()

        respuesta = messagebox.askretrycancel(
            "Archivo de configuración no encontrado",
            f"No se encontró el archivo {archivo_ini}. ¿Desea seleccionarlo manualmente o crear uno nuevo?"
        )

        if not respuesta:
            messagebox.showinfo("Operación cancelada", "No se seleccionó ningún archivo.")
            temporal.destroy()
            return

        ruta_config = filedialog.asksaveasfilename(
            title=f"Seleccione o cree el archivo {archivo_ini}",
            filetypes=[("Archivo de configuración", "*.ini")],
            initialdir=base_dir,
            defaultextension=".ini"
        )

        if not ruta_config:
            messagebox.showwarning("Selección inválida", "No seleccionó ningún archivo. Inténtelo de nuevo o cancele.")
            temporal.destroy()
        else:
            logging.info(f"Archivo de configuración seleccionado/creado: {ruta_config}")
            temporal.destroy()
            break

    config = configparser.ConfigParser()
    if os.path.exists(ruta_config):
        config.read(ruta_config)

    if 'Configuracion' not in config:
        config['Configuracion'] = {}

    config['Configuracion'][config_key] = config_value

    try:
        with open(ruta_config, 'w') as configfile:
            config.write(configfile)
        logging.info(f"Configuración '{config_key}' guardada exitosamente en {ruta_config}.")
    except Exception as e:
        logging.error(f"Error al guardar la configuración '{config_key}': {e}")


def calcular_hash(archivo: str) -> str:
    """
    Calcula el hash SHA-256 de un archivo dado, leyendo en bloques para optimizar el uso de memoria.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(archivo, 'rb') as f:
            for bloque in iter(lambda: f.read(4096), b""):
                sha256_hash.update(bloque)
    except Exception as e:
        logging.error(f"Error al calcular hash para {archivo}: {e}")
        return ""
    return sha256_hash.hexdigest()


def encontrar_y_eliminar_duplicados(directorio: str) -> list:
    """
    Encuentra y elimina archivos duplicados en un directorio basado en el hash de su contenido.
    """
    hashes = {}
    contador_duplicados = 0
    contador_unicos = 0

    for archivo in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, archivo)
        if os.path.isfile(ruta_completa) and archivo.endswith('.xml'):
            hash_archivo = calcular_hash(ruta_completa)
            if not hash_archivo:
                continue  # Si hubo error calculando el hash, saltar este archivo

            if hash_archivo in hashes:
                try:
                    os.remove(ruta_completa)
                    contador_duplicados += 1
                    logging.info(f"Archivo duplicado eliminado: {ruta_completa}")
                except OSError as e:
                    logging.error(f"Error al eliminar {archivo}: {e}")
            else:
                hashes[hash_archivo] = ruta_completa
                contador_unicos += 1

    mensajes = [
        f"Se han eliminado {contador_duplicados} archivos duplicados.",
        f"Quedan {contador_unicos} archivos únicos en el directorio."
    ]
    logging.info("Proceso de eliminación de duplicados finalizado.")
    return mensajes

