"""Punto de entrada de la aplicación.

Responsabilidades:
- Inicializar logging
- Crear/verificar esquema de base de datos
- Probar conexión
- Lanzar la interfaz gráfica
"""

from logger_config import logger
from ui.main_window import run_app


def main() -> None:
    logger.info("Aplicación iniciando")
    # La creación de tablas y la prueba de conexión se difieren al arranque de la UI
    run_app()

    logger.info("Aplicación finalizada")

if __name__ == "__main__":
    main()
 