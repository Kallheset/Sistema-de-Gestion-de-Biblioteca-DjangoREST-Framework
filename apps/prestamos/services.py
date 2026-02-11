from django.utils import timezone
from django.db import transaction
from .models import Prestamo, MAX_LIBROS_POR_USUARIO
from apps.libros.models import Libro
from apps.common.exceptions import BusinessLogicError, ResourceNotFoundError

class PrestamoService:
    @staticmethod
    @transaction.atomic
    def crear_prestamo(usuario, libro, dias_prestamo=7):
        """
        Crea un nuevo préstamo validando disponibilidad y límites.
        """
        # 1. Validar disponibilidad del libro
        if not libro.disponible or libro.stock <= 0:
            raise BusinessLogicError(f'El libro "{libro.titulo}" no está disponible.')

        # 2. Validar límite de préstamos del usuario
        prestamos_activos = Prestamo.objects.filter(
            usuario=usuario,
            fecha_devolucion__isnull=True
        ).count()
        
        if prestamos_activos >= MAX_LIBROS_POR_USUARIO:
            raise BusinessLogicError(f'El usuario ha alcanzado el límite de {MAX_LIBROS_POR_USUARIO} préstamos.')

        # 3. Calcular fecha de devolución esperada
        fecha_esperada = timezone.now().date() + timezone.timedelta(days=dias_prestamo)

        # 4. Crear el préstamo
        prestamo = Prestamo.objects.create(
            usuario=usuario,
            libro=libro,
            fecha_devolucion_esperada=fecha_esperada
        )

        # 5. Actualizar stock del libro
        libro.stock -= 1
        if libro.stock == 0:
            libro.disponible = False
        libro.save()

        return prestamo

    @staticmethod
    @transaction.atomic
    def devolver_libro(prestamo):
        """
        Procesa la devolución de un libro.
        """
        if prestamo.devuelto:
            raise BusinessLogicError('Este libro ya fue devuelto.')

        # 1. Registrar fecha de devolución
        prestamo.fecha_devolucion = timezone.now().date()
        prestamo.save()

        # 2. Restaurar stock
        libro = prestamo.libro
        libro.stock += 1
        libro.disponible = True
        libro.save()

        return prestamo
