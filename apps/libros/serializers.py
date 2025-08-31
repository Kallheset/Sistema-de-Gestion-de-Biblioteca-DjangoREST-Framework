from rest_framework import serializers
from apps.autores.models import Autor
from .models import Categoria, Libro
from apps.autores.serializers import AutorSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class LibroSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        source='autor',
        write_only=True
    )
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Libro
        fields = [
            'id', 'titulo', 'autor', 'autor_id', 'isbn',
            'categoria', 'categoria_id', 'fecha_publicacion',
            'disponible', 'imagen', 'descripcion', 'paginas',
            'calificacion', 'stock'
        ]
        read_only_fields = ['disponible']

    def validate_isbn(self, value):
        if len(value) != 13 or not value.isdigit():
            raise serializers.ValidationError('El ISBN debe tener 13 dígitos numéricos.')
        return value
