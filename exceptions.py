"""
Módulo de excepciones personalizadas para la aplicación.
Define excepciones específicas del dominio para manejar errores de forma clara y profesional.
Esto permite que la UI muestre mensajes útiles al usuario y facilita la depuración.
"""

class AppError(Exception):
    """
    Excepción base para toda la aplicación.
    Todas las excepciones personalizadas heredan de esta clase.
    Permite capturar cualquier error de la app de forma genérica.
    """
    pass

class ErrorDeBaseDeDatos(AppError):
    """
    Excepción para errores relacionados con la base de datos.
    Se lanza cuando ocurren problemas de conexión, consultas fallidas, o errores de SQL.
    Ejemplos: problemas de permisos, base de datos corrupta, consultas mal formadas.
    """
    pass

class UsuarioYaExiste(AppError):
    """
    Excepción que se lanza cuando se intenta crear un usuario que ya existe.
    Ocurre cuando se viola la restricción única en la base de datos.
    Permite mostrar un mensaje claro al usuario: "El usuario ya existe".
    """
    pass

class RegistroDuplicado(AppError):
    """
    Excepción que se lanza cuando se intenta registrar un día remoto que ya está asignado.
    Ocurre cuando se viola la restricción única en la tabla de registros.
    Permite mostrar un mensaje claro al usuario: "Ya existe un registro para ese día".
    """
    pass
