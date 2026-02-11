from django.db import transaction
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
