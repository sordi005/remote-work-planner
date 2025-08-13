"""Excepciones de dominio de la aplicación (mensajes claros y manejables en UI)."""

class AppError(Exception):
    """Base de todas las excepciones de la app."""
    pass

class ErrorDeBaseDeDatos(AppError):
    """Errores de conexión/consulta/SQL en la base de datos."""
    pass

class UsuarioYaExiste(AppError):
    """Restricción de unicidad al crear usuario (docket duplicado)."""
    pass

class RegistroDuplicado(AppError):
    """Restricción de unicidad al crear registro (mismo usuario y fecha)."""
    pass
