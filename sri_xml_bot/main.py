import logging
from sri_xml_bot.librerias.gui import Application
from sri_xml_bot.librerias.utils import ruta_relativa_recurso


def configurar_logging():
    """
    Configura el sistema de logging para la aplicación.
    """
    ruta_archivo_log = ruta_relativa_recurso("archivos/app.log", [("Archivos de log", "*.log")])
    logging.basicConfig(
        filename=ruta_archivo_log,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info('Logging configurado correctamente.')

def main():
    """
    Función principal que inicia la aplicación.
    """
    configurar_logging()
    try:
        app = Application()
        app.run()
    except Exception as e:
        logging.exception("Ocurrió un error al iniciar la aplicación.")
        raise e

if __name__ == "__main__":
    main()
