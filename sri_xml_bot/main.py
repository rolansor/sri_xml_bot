import logging
import logging.handlers
import sys
from sri_xml_bot.gui import Application
from sri_xml_bot.librerias.utils import ruta_relativa_recurso

def configurar_logging():
    """
    Configura el sistema de logging para la aplicación,
    incluyendo rotación de archivos y salida a consola.
    """

    # Construimos la ruta del archivo de log
    ruta_archivo_log = ruta_relativa_recurso("../archivos/app.log", [("Archivos de log", "*.log")])

    # Obtenemos el logger raíz
    logger = logging.getLogger()
    # Establecemos el nivel de logging para el logger raíz
    logger.setLevel(logging.INFO)

    # Para evitar múltiples handlers en caso de que configuremos el logger varias veces
    if not logger.handlers:
        # Handler para rotar el archivo de log si excede cierto tamaño
        archivo_handler = logging.handlers.RotatingFileHandler(
            filename=ruta_archivo_log,
            maxBytes=5_000_000,  # 5 MB
            backupCount=5,  # Número de archivos de respaldo
            encoding='utf-8'
        )

        # Formato de los mensajes en el log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        archivo_handler.setFormatter(formatter)

        # Handler para enviar logs a la consola (útil durante el desarrollo)
        consola_handler = logging.StreamHandler(sys.stdout)
        consola_handler.setLevel(logging.DEBUG)  # Ajusta el nivel según necesidad
        consola_handler.setFormatter(formatter)

        # Agregamos ambos handlers al logger
        logger.addHandler(archivo_handler)
        logger.addHandler(consola_handler)

    logger.info(f"Logging configurado correctamente. Archivo de log: {ruta_archivo_log}")


def main():
    """
    Punto de entrada principal de la aplicación.
    Maneja la configuración inicial y ejecuta la GUI.
    Captura excepciones no controladas y las registra.
    """
    configurar_logging()
    try:
        app = Application()
        app.run()
    except Exception as e:
        logging.exception("Ocurrió un error al iniciar la aplicación.")
        sys.exit(1)

if __name__ == "__main__":
    main()
