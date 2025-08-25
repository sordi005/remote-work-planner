"""Configuración centralizada de logging.

Características:
- Rotación diaria automática (medianoche) con retención.
- Detección automática del entorno: producción si está empaquetado (PyInstaller),
  desarrollo si se ejecuta desde código.
- Salida a archivo y consola (menos verbosa en producción).
- Captura excepciones no controladas al log.
"""
import logging
import logging.handlers
import sys
from config import LOG_DIR


# === Configuración de nivel según entorno (sin variables de entorno) ===
APP_ENV = "production" if getattr(sys, "frozen", False) else "development"
DEFAULT_LEVEL = "INFO" if APP_ENV == "production" else "DEBUG"
LOG_LEVEL = getattr(logging, DEFAULT_LEVEL, logging.INFO)


def _configure_root_logger() -> None:
    """Configura el logger raíz con rotación diaria y consola.

    Idempotente: limpia handlers previos para evitar duplicados.
    """
    root = logging.getLogger()
    # Limpia handlers previos si los hubiera
    for h in list(root.handlers):
        root.removeHandler(h)

    root.setLevel(LOG_LEVEL)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler de archivo con rotación diaria
    file_path = LOG_DIR / "app.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(file_path), when="midnight", backupCount=30, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(LOG_LEVEL)
    root.addHandler(file_handler)

    # Handler de consola (menos verboso en producción)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console_level = logging.WARNING if APP_ENV == "production" else LOG_LEVEL
    console.setLevel(console_level)
    root.addHandler(console)


def _install_excepthook() -> None:
    """Registra un hook para capturar excepciones no controladas en el log."""
    def _handle(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            # Respetar Ctrl+C en consola
            return sys.__excepthook__(exc_type, exc_value, exc_tb)
        logging.getLogger("GestorEmpleados").exception(
            "Excepción no capturada", exc_info=(exc_type, exc_value, exc_tb)
        )

    sys.excepthook = _handle


def _capture_warnings() -> None:
    """Redirige warnings.warn al sistema de logging."""
    logging.captureWarnings(True)


# Aplicar configuración al importar el módulo
_configure_root_logger()
_install_excepthook()
_capture_warnings()


# Logger de conveniencia para la app
logger = logging.getLogger("GestorEmpleados")
