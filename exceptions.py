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

# Nuevas excepciones específicas de reglas de negocio

class DiaNoPermitido(AppError):
    """El día seleccionado no está permitido (lunes o fin de semana)."""
    pass

class YaRegistradoEstaSemana(AppError):
    """El usuario ya cuenta con un registro en la semana actual."""
    pass

class NoHayRegistroEstaSemana(AppError):
    """No existe registro en la semana actual para poder cambiarlo."""
    pass

class FechaFueraDeSemanaActual(AppError):
    """La fecha no corresponde a la semana actual."""
    pass