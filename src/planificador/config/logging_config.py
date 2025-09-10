"""
Configuración del sistema de logging estructurado utilizando Loguru.

Este módulo proporciona una configuración centralizada para el logging
en toda la aplicación, asegurando que los logs sean consistentes,
estructurados (en formato JSON) y fáciles de analizar.

Funciones:
    setup_logging: Configura y activa el logger de Loguru.
"""

import sys
import logging
from pathlib import Path
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Handler para interceptar los logs estándar de Python y redirigirlos a Loguru.
    """
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emite un registro de log.

        Args:
            record: El registro de log a emitir.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: Path = Path("logs"),
    serialize: bool = True
) -> None:
    """
    Configura el logger de Loguru para la aplicación.

    Esta función establece los handlers para la salida a consola y a fichero,
    con formato estructurado (JSON) y rotación de archivos.

    Args:
        log_level: El nivel mínimo de log a registrar (e.g., "INFO", "DEBUG").
        log_dir: El directorio donde se guardarán los ficheros de log.
        serialize: Si es True, los logs en fichero se guardarán en formato JSON.
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    # Formato para la consola, más legible para humanos
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Configuración base del logger
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format=console_format,
        colorize=True,
    )

    # Configuración para el fichero de log
    log_file = log_dir / "planificador.log"
    logger.add(
        log_file,
        level=log_level,
        serialize=serialize, # Guardar en formato JSON
        enqueue=True,        # Hacer el logging asíncrono y seguro para threads
        backtrace=True,
        diagnose=True,
    )

    # Interceptar logs de librerías estándar
    # logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.info("Logging configurado correctamente (con intercepción deshabilitada temporalmente).")