from rest_framework.exceptions import APIException
from rest_framework import status

class BibliotecaBaseError(Exception):
    """Excepción base para todos los errores de la aplicación."""
    message = "Ha ocurrido un error inesperado."
    
    def __init__(self, message=None, extra=None):
        self.message = message or self.message
        self.extra = extra or {}
        super().__init__(self.message)

class BusinessLogicError(BibliotecaBaseError):
    """Errores relacionados con la lógica de negocio (ej. stock insuficiente)."""
    message = "Error en la lógica de negocio."

class ValidationError(BibliotecaBaseError):
    """Errores de validación de datos."""
    message = "Los datos proporcionados no son válidos."

class ResourceNotFoundError(BibliotecaBaseError):
    """Cuando un recurso solicitado no existe."""
    message = "El recurso solicitado no fue encontrado."

# Exception Handler para DRF (opcional pero recomendado)
def biblioteca_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    from rest_framework.response import Response
    
    # Primero intentamos con el handler de DRF
    response = exception_handler(exc, context)
    
    # Si es una de nuestras excepciones personalizadas
    if isinstance(exc, BibliotecaBaseError):
        data = {
            'error': exc.message,
            'details': exc.extra
        }
        
        # Determinar status code
        if isinstance(exc, ResourceNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            
        return Response(data, status=status_code)
    
    return response
