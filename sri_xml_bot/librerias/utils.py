import configparser
import os
import sys
from tkinter import Tk, messagebox, filedialog
import re
import logging
import hashlib


def centrar_ventana(titulo, ventana, ancho=800, alto=500):
    """
    Centra una ventana en la pantalla con un tamaño fijo.

    :param ventana: Instancia de Tkinter window (Tk o Toplevel).
    :param ancho: Ancho de la ventana.
    :param alto: Alto de la ventana.
    """
    ventana.title(titulo)
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.resizable(False, False)


# Función para obtener la ruta de un recurso, manejando el entorno de PyInstaller
def ruta_relativa_recurso(relativa, filetypes=[("Archivos de texto", "*.txt")]):
    """
    Retorna la ruta correcta de un recurso en el mismo directorio desde el que se ejecuta el .exe.
    Si no se encuentra, abre un diálogo para que el usuario seleccione el archivo manualmente.

    Args:
        relativa: La ruta relativa del recurso que se quiere acceder.
        filetypes: Lista de tuplas para filtrar el tipo de archivo en el cuadro de diálogo.

    Returns:
        str or None: La ruta absoluta del recurso o None si no se selecciona ningún archivo.
    """

    # Obtener el directorio de ejecución
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    ruta_archivo = os.path.join(base_dir, relativa)

    # Verificar si el archivo existe en la ubicación esperada
    while not os.path.exists(ruta_archivo):
        # Crear la ventana principal de Tk
        temporal = Tk()
        temporal.withdraw()  # Oculta la ventana principal de Tk
        file_name = os.path.basename(ruta_archivo)

        # Advertencia al usuario y opciones para seleccionar o cerrar la aplicación
        respuesta = messagebox.askretrycancel(
            "Archivo no encontrado",
            f"No se encontró el archivo {file_name}. ¿Desea intentar seleccionarlo manualmente?"
        )

        # Si el usuario cancela, se cierra la aplicación
        if not respuesta:
            messagebox.showinfo("Operación cancelada", "No se seleccionó ningún archivo. Cerrando aplicación.")
            temporal.destroy()
            sys.exit(1)

        # Permitir que el usuario seleccione el archivo manualmente
        ruta_archivo = filedialog.askopenfilename(
            title=f"Seleccione el archivo {file_name}",
            filetypes=filetypes,
            initialdir=base_dir
        )

        # Si el usuario no selecciona ningún archivo, se vuelve a mostrar la advertencia
        if not ruta_archivo:
            messagebox.showwarning("Selección inválida", "No seleccionó ningún archivo. Inténtelo de nuevo o cancele.")
            temporal.destroy()
        else:
            # Si selecciona un archivo, cerramos la ventana temporal y devolvemos la ruta
            temporal.destroy()
            break

    return ruta_archivo


def separar_tipo_y_serie(comprobante):
    """
    Funcion que se utiliza para separar tipo y serie de la tabla de la consulta de recibidos del sri.
    Separa el tipo y la serie del comprobante de un string en el formato tipo documento 000-000-00000000
    """
    match = re.match(r"(.+?)\s+(\d{3}-\d{3}-\d{9})", comprobante)
    return (match.group(1).strip(), match.group(2).strip()) if match else (None, None)


def cargar_configuracion_ini():
    """
    Carga todas las configuraciones desde un archivo .ini y las devuelve en un diccionario.
    """
    # Configuración por defecto
    configuraciones = {
        "nombre_archivo": "ruc_secuencial",
        "ruta_guardado": "Año/Mes/RUC/RecEmi/XML/TipoDocumento",
        "ruc_actual": "9999999999999",
        "ruta_chromedriver": "archivos/chromedriver.exe",
        "ruta_logos": "archivos/logo.png",
        "ruta_rucs": "archivos/rucs.txt",
        "ruta_logs": "archivos/app.log",
    }

    # Ruta del archivo de configuración
    archivo_ini = 'archivos/configuraciones.ini'
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    ruta_config = os.path.join(base_dir, archivo_ini)

    # Leer el archivo de configuración si existe
    if os.path.exists(ruta_config):
        config = configparser.ConfigParser()
        try:
            config.read(ruta_config)
            if 'Configuracion' in config:
                for key in configuraciones.keys():
                    configuraciones[key] = config.get("Configuracion", key, fallback=configuraciones[key])
            else:
                logging.warning("La sección 'Configuracion' no se encontró en el archivo. Usando valores predeterminados.")
        except configparser.Error as e:
            logging.error(f"Error al leer el archivo de configuración: {e}. Usando valores predeterminados.")
    else:
        logging.warning(f"Archivo de configuración '{archivo_ini}' no encontrado. Usando valores predeterminados.")

    return configuraciones


def guardar_configuracion_ini(config_key, config_value):
    """
    Guarda solo una configuración en el archivo .ini.

    Args:
        config_key (str): Clave de la configuración a actualizar.
        config_value (str): Nuevo valor de la configuración.
    """
    # Definir el nombre del archivo de configuración
    archivo_ini = 'archivos/configuraciones.ini'
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    ruta_config = os.path.join(base_dir, archivo_ini)

    # Verificar si el archivo de configuración existe
    while not os.path.exists(ruta_config):
        # Crear una ventana de Tk para el diálogo
        temporal = Tk()
        temporal.withdraw()  # Ocultar la ventana principal

        # Solicitar al usuario seleccionar o crear el archivo de configuración
        respuesta = messagebox.askretrycancel(
            "Archivo de configuración no encontrado",
            f"No se encontró el archivo {archivo_ini}. ¿Desea seleccionarlo manualmente o crear uno nuevo?"
        )

        # Si el usuario cancela, salir del programa
        if not respuesta:
            messagebox.showinfo("Operación cancelada", "No se seleccionó ningún archivo.")
            temporal.destroy()

        # Permitir al usuario seleccionar un archivo de configuración
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
            temporal.destroy()
            break

    # Cargar el archivo existente o crear uno nuevo si no existe
    config = configparser.ConfigParser()
    if os.path.exists(ruta_config):
        config.read(ruta_config)

    if 'Configuracion' not in config:
        config['Configuracion'] = {}

    # Actualizar solo la configuración especificada
    config['Configuracion'][config_key] = config_value

    # Guardar el archivo de configuración actualizado
    try:
        with open(ruta_config, 'w') as configfile:
            config.write(configfile)
        logging.info(f"Configuración '{config_key}' guardada exitosamente.")
    except Exception as e:
        logging.error(f"Error al guardar la configuración '{config_key}': {e}")


def calcular_hash(archivo):
    """
    Calcula el hash SHA-256 de un archivo dado para identificar duplicados.

    Args:
        archivo (str): Ruta completa del archivo.

    Returns:
        str: Hash SHA-256 del contenido del archivo.
    """
    with open(archivo, 'rb') as f:
        contenido = f.read()
        return hashlib.sha256(contenido).hexdigest()


def encontrar_y_eliminar_duplicados(directorio):
    """
    Encuentra y elimina archivos duplicados en un directorio basado en el hash de su contenido.

    Args:
        directorio (str): Ruta del directorio donde se buscarán y eliminarán los duplicados.

    Returns:
        list: Lista de mensajes sobre la operación realizada, incluyendo el número de duplicados eliminados y archivos únicos restantes.
    """
    # Diccionario para almacenar el hash de cada archivo y su nombre
    hashes = {}
    # Contador de archivos duplicados eliminados
    contador_duplicados = 0
    # Contador de archivos únicos
    contador_unicos = 0

    # Iterar sobre todos los archivos en el directorio
    for archivo in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, archivo)

        # Comprobar si es un archivo XML
        if os.path.isfile(ruta_completa) and archivo.endswith('.xml'):
            # Calcular el hash del archivo actual
            hash_archivo = calcular_hash(ruta_completa)

            # Verificar si el hash ya existe, lo que indica un duplicado
            if hash_archivo in hashes:
                try:
                    os.remove(ruta_completa)
                    contador_duplicados += 1
                except OSError as e:
                    logging.error(f"Error al eliminar {archivo}: {e}")
            else:
                hashes[hash_archivo] = ruta_completa  # Almacenar el hash y su ruta completa
                contador_unicos += 1

    # Crear los mensajes finales en una lista
    mensajes = [f"Se han eliminado {contador_duplicados} archivos duplicados.",
        f"Quedan {contador_unicos} archivos únicos en el directorio."]

    return mensajes

