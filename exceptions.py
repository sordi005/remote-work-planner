class AppError(Exception):
    """Excepción base para la aplicación."""
    pass

class ErrorDeBaseDeDatos(AppError):
    """Errores relacionados con la base de datos."""
    pass

class UsuarioYaExiste(AppError):
    """Cuando se intenta crear un usuario que ya existe."""
    pass

class RegistroDuplicado(AppError):
    """Cuando se intenta registrar un día ya asignado."""
    pass
