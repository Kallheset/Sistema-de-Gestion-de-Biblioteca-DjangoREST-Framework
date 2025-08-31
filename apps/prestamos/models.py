from django.db import models
from django.contrib.auth.models import User
from apps.libros.models import Libro
from django.utils import timezone
from django.core.exceptions import ValidationError

# Constantes
MAX_LIBROS_POR_USUARIO = 3

# Create your models here.

class Prestamo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    fecha_devolucion_esperada = models.DateField()
    
    class Meta:
        ordering = ['-fecha_prestamo']
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
    
    def __str__(self):
        return f'Prestamo de {self.libro.titulo} a {self.usuario.username}'
    
    @property
    def devuelto(self):
        return self.fecha_devolucion is not None
    
    @classmethod
    def libros_prestados_por_usuario(cls, usuario):
        return cls.objects.filter(
            usuario=usuario,
            fecha_devolucion__isnull=True
        ).count()

    def clean(self):
        errors = {}
        
        # Validar disponibilidad del libro
        if not self.pk and not self.libro.disponible:
            errors['libro'] = 'El libro no está disponible para préstamo.'
        
        # Validar límite de préstamos
        if not self.pk and Prestamo.libros_prestados_por_usuario(self.usuario) >= MAX_LIBROS_POR_USUARIO:
            errors['usuario'] = 'El usuario ya alcanzó el límite de préstamos permitidos.'
        
        # Validar fecha de devolución esperada
        # Solo se considera inválida si la fecha ya pasó y el préstamo aún no fue devuelto
        if (
            self.fecha_devolucion_esperada
            and self.fecha_devolucion_esperada < timezone.now().date()
            and self.fecha_devolucion is None
        ):
            errors['fecha_devolucion_esperada'] = 'La fecha de devolución esperada no puede ser en el pasado.'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:  # Solo para nuevos préstamos
            # Reducir el stock
            self.libro.stock -= 1
            # Si el stock llega a 0, marcar como no disponible
            if self.libro.stock == 0:
                self.libro.disponible = False
            self.libro.save()
        super().save(*args, **kwargs)

    def devolver(self):
        if self.fecha_devolucion:
            raise ValidationError({'fecha_devolucion': 'El libro ya fue devuelto.'})
        
        self.fecha_devolucion = timezone.now().date()
        # Incrementar el stock y marcar como disponible
        self.libro.stock += 1
        self.libro.disponible = True
        self.libro.save()
        self.save()
