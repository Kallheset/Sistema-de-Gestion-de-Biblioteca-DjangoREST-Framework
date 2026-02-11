from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Prestamo, MAX_LIBROS_POR_USUARIO
from django.contrib.auth.models import User
from apps.libros.models import Libro
from apps.libros.serializers import LibroSerializer
from .services import PrestamoService
from apps.common.exceptions import BibliotecaBaseError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
           

class PrestamoSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    libro = LibroSerializer(read_only=True)
    libro_id = serializers.IntegerField(write_only=True, required=True)
    dias_prestamo = serializers.IntegerField(write_only=True, required=False, default=7)

    class Meta:
        model = Prestamo
        fields = ['id', 'usuario', 'libro', 'libro_id', 'fecha_prestamo', 'fecha_devolucion_esperada', 'fecha_devolucion', 'dias_prestamo']
        read_only_fields = ['usuario', 'fecha_prestamo', 'fecha_devolucion_esperada', 'fecha_devolucion']

    def create(self, validated_data):
        libro_id = validated_data.get('libro_id')
        dias_prestamo = validated_data.get('dias_prestamo', 7)
        usuario = self.context['request'].user
        
        try:
            libro = Libro.objects.get(id=libro_id)
            return PrestamoService.crear_prestamo(usuario, libro, dias_prestamo)
        except Libro.DoesNotExist:
            raise serializers.ValidationError({'libro_id': 'El libro especificado no existe.'})
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)

    def update(self, instance, validated_data):
        try:
            return PrestamoService.devolver_libro(instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)
