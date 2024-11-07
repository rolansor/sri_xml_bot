import configparser
import os
import sys
from tkinter import Tk, messagebox, filedialog
import re
import logging
import hashlib


def centrar_ventana(ventana, ancho=800, alto=500):
    """
    Centra una ventana en la pantalla con un tamaño fijo.

    :param ventana: Instancia de Tkinter window (Tk o Toplevel).
    :param ancho: Ancho de la ventana.
    :param alto: Alto de la ventana.
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


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


def guardar_configuracion_ini(nombre_archivo, ruta_guardado):
    """
    Guarda la configuración en un archivo .ini. Si el archivo no existe, permite al usuario seleccionarlo o crearlo.

    Args:
        nombre_archivo (str): Nombre del archivo seleccionado para el XML.
        ruta_guardado (str): Ruta de guardado personalizada.
    """
    # Definir el nombre del archivo de configuración
    archivo_ini = 'archivos/configuraciones.ini'

    # Obtener la ruta de la ubicación del archivo
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

    # Guardar la configuración en el archivo .ini
    config = configparser.ConfigParser()
    config.read(ruta_config)

    # Actualizar solo las configuraciones necesarias
    if 'Configuracion' not in config:
        config['Configuracion'] = {}

    config['Configuracion']['nombre_archivo'] = nombre_archivo
    config['Configuracion']['ruta_guardado'] = ruta_guardado

    # Guardar la configuración actualizada en el archivo .ini
    try:
        with open(ruta_config, 'w') as configfile:
            config.write(configfile)

        messagebox.showinfo("Configuración Guardada", "La configuración ha sido guardada exitosamente.")
        logging.info("Configuración guardada exitosamente en configuraciones.ini.")

    except Exception as e:
        logging.error(f"Error al guardar la configuración: {e}")

def cargar_configuracion_ini():
    """
    Carga la configuración desde un archivo .ini y establece valores en variables globales.
    Si el archivo no existe, se registran valores predeterminados.

    Returns:
        tuple: Contiene (nombre_archivo, ruta_guardado, ruc_actual) cargados o predeterminados.
    """
    # Valores predeterminados
    nombre_archivo = "clave_acceso"
    ruta_guardado = "Año/Mes/RUC/RecEmi/XML/TipoDocumento"
    ruc_actual = "9999999999999"

    # Ruta del archivo de configuración
    archivo_ini = 'archivos/configuraciones.ini'
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    ruta_config = os.path.join(base_dir, archivo_ini)

    # Verificar si el archivo de configuración existe y cargar su contenido
    if os.path.exists(ruta_config):
        config = configparser.ConfigParser()
        try:
            config.read(ruta_config)
            if 'Configuracion' in config:
                nombre_archivo = config.get("Configuracion", "nombre_archivo", fallback=nombre_archivo)
                ruta_guardado = config.get("Configuracion", "ruta_guardado", fallback=ruta_guardado)
                ruc_actual = config.get("Configuracion", "ruc_actual", fallback=ruc_actual)
            else:
                logging.warning(
                    "La sección 'Configuracion' no se encontró en el archivo. Usando valores predeterminados.")
        except configparser.Error as e:
            logging.error(f"Error al leer el archivo de configuración: {e}. Usando valores predeterminados.")
    else:
        logging.warning(f"Archivo de configuración '{archivo_ini}' no encontrado. Usando valores predeterminados.")

    return nombre_archivo, ruta_guardado, ruc_actual


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
        list: Lista de mensajes de log sobre la operación realizada, incluyendo el número de duplicados eliminados.
    """
    # Diccionario para almacenar el hash de cada archivo y su nombre
    hashes = {}
    # Lista para almacenar el nombre de los archivos duplicados encontrados
    duplicados = []
    # Lista de mensajes de log para informar sobre la operación
    mensajes = []

    # Iterar sobre todos los archivos en el directorio
    for archivo in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, archivo)

        # Comprobar si es un archivo XML
        if os.path.isfile(ruta_completa) and archivo.endswith('.xml'):
            # Calcular el hash del archivo actual
            hash_archivo = calcular_hash(ruta_completa)

            # Verificar si el hash ya existe, lo que indica un duplicado
            if hash_archivo in hashes:
                duplicados.append(ruta_completa)  # Añadir la ruta completa del duplicado
            else:
                hashes[hash_archivo] = ruta_completa  # Almacenar el hash y su ruta completa

    # Eliminar los archivos duplicados encontrados
    for archivo in duplicados:
        try:
            os.remove(archivo)
            mensajes.append(f'Eliminado archivo duplicado: {archivo}')
        except OSError as e:
            mensajes.append(f'Error al eliminar {archivo}: {e}')

    # Añadir mensaje final sobre la operación
    mensajes.append(f'Se han eliminado {len(duplicados)} archivos duplicados en total.')

    return mensajes
