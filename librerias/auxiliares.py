import os
import sys
from tkinter import messagebox, filedialog, Tk, Toplevel


# Función para centrar la ventana en la pantalla
def centrar_ventana(ventana):
    """
    Centra la ventana dada en la pantalla.
    Calcula la posición adecuada en función del tamaño de la pantalla del usuario.

    Args:
        ventana: La ventana de Tkinter que se desea centrar.
    """
    ventana.update_idletasks()  # Asegura que se actualicen las dimensiones antes de calcular el centrado.
    ancho = 400  # Ancho fijo de la ventana.
    alto = 900  # Alto fijo de la ventana.

    # Calcula la posición X e Y para centrar la ventana
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)

    # Define el tamaño y posición de la ventana en la pantalla
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
    ventana.deiconify()  # Asegura que la ventana se muestre si estaba oculta.


# Función auxiliar para abrir una ventana secundaria
def abrir_ventana_secundaria(titulo, root, comando_cerrar=None):
    """
    Abre una ventana secundaria (Toplevel) bloqueando la interacción con la ventana principal.

    Args:
        titulo: El título de la ventana secundaria.
        root: La ventana principal (Tk).
        comando_cerrar: (Opcional) Una función que se ejecuta cuando se cierra la ventana secundaria.

    Returns:
        nueva_ventana: La nueva ventana secundaria (Toplevel).
    """
    root.withdraw()  # Ocultar la ventana principal mientras la secundaria está abierta.

    # Crear la ventana secundaria
    nueva_ventana = Toplevel(root)
    nueva_ventana.title(titulo)  # Establecer el título de la ventana.
    centrar_ventana(nueva_ventana)
    nueva_ventana.grab_set()  # Bloquear interacción con otras ventanas.
    nueva_ventana.focus_set()  # Enfocar la ventana secundaria.

    # Si se proporciona un comando para cerrar, asignarlo al evento de cierre de ventana
    if comando_cerrar:
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: comando_cerrar(nueva_ventana, root))

    return nueva_ventana  # Retorna la nueva ventana.


# Función para cerrar una ventana secundaria y restaurar la ventana principal
def cerrar_ventana_secundaria(ventana, root):
    """
    Cierra una ventana secundaria y restaura la ventana principal.

    Args:
        ventana: La ventana secundaria que se desea cerrar.
        root: La ventana principal (Tk) que se desea mostrar nuevamente.
    """
    ventana.grab_release()  # Liberar el bloqueo de la ventana.
    ventana.destroy()  # Cerrar la ventana secundaria.
    root.deiconify()  # Mostrar la ventana principal nuevamente.


# Función para cerrar la aplicación de manera segura
def cerrar_aplicacion(root):
    """
    Solicita confirmación al usuario antes de cerrar la aplicación.

    Args:
        root: La ventana principal de Tkinter (Tk).
    """
    respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas salir?")  # Pregunta de confirmación.
    if respuesta:
        root.destroy()  # Si el usuario confirma, se cierra la aplicación.


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
    if not os.path.exists(ruta_archivo):
        # Mostrar advertencia y abrir cuadro de diálogo para selección manual
        file_name = os.path.basename(ruta_archivo)
        # Crear la ventana principal de Tk
        temporal = Tk()
        temporal.withdraw()  # O
        messagebox.showwarning("Archivo no encontrado",
                               f"No se encontró el archivo {file_name}. Seleccione el archivo manualmente.")
        ruta_archivo = filedialog.askopenfilename(
            title=f"Seleccione el archivo {file_name}",
            filetypes=filetypes,
            initialdir=base_dir
        )
        # Si el usuario no selecciona ningún archivo, retornar None
        if not ruta_archivo:
            print("No se seleccionó ningún archivo.")
            temporal.destroy()
            sys.exit(1)
        temporal.destroy()
    return ruta_archivo


def cargar_rucs():
    rucs = {}

    # Ruta del archivo junto al ejecutable
    ruta_archivo = ruta_relativa_recurso('archivos/rucs.txt', filetypes=[("Archivos de texto", "*.txt")])

    try:
        with open(ruta_archivo, 'r') as archivo:
            index = 1  # Índice inicial
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
                    rucs[index] = {'ruc': ruc, 'nombre': nombre, 'contrasena': clave}
                    index += 1  # Incrementar índice para la siguiente entrada
                else:
                    print(f"Línea malformada: {linea}")
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return rucs
