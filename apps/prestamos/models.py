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
        return f'Préstamo de {self.libro.titulo} a {self.usuario.username}'
    
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
        # Mantenemos validaciones básicas para compatibilidad con el Admin
        errors = {}
        
        if not self.pk and not self.libro.disponible:
            errors['libro'] = 'El libro no está disponible para préstamo.'
        
        if not self.pk and Prestamo.libros_prestados_por_usuario(self.usuario) >= MAX_LIBROS_POR_USUARIO:
            errors['usuario'] = 'El usuario ya alcanzó el límite de préstamos permitidos.'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
