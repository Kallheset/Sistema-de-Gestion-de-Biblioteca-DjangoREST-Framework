from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Libro

class LibroService:
    @staticmethod
    @transaction.atomic
    def crear_libro(datos, imagen=None):
        """
        Crea un nuevo libro encapsulando la lógica de persistencia.
        """
        libro = Libro.objects.create(
            titulo=datos['titulo'],
            autor_id=datos['autor'],
            categoria_id=datos['categoria'],
            isbn=datos['isbn'],
            descripcion=datos.get('descripcion', ''),
            fecha_publicacion=datos['fecha_publicacion'],
            stock=datos.get('stock', 1)
        )
        
        if imagen:
            libro.imagen = imagen
            libro.save()
            
        return libro
    
    @staticmethod
    @transaction.atomic
    def actualizar_stock(libro, cantidad):
        """
        Actualiza el stock de un libro y su disponibilidad.
        
        Args:
            libro: Instancia del libro a actualizar
            cantidad: Cantidad a sumar (positiva) o restar (negativa)
        
        Raises:
            ValidationError: Si el stock resultante sería negativo
        """
        nuevo_stock = libro.stock + cantidad
        
        if nuevo_stock < 0:
            raise ValidationError(
                f'Stock insuficiente. Stock actual: {libro.stock}, cantidad solicitada: {abs(cantidad)}'
            )
        
        libro.stock = nuevo_stock
        libro.disponible = nuevo_stock > 0
        libro.save()
        
        return libro
