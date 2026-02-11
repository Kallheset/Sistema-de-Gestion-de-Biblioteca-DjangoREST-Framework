import pytest
from django.core.exceptions import ValidationError
from apps.libros.models import Libro, Categoria
from apps.autores.models import Autor
from apps.libros.services import LibroService

@pytest.mark.django_db
class TestLibroService:
    @pytest.fixture
    def setup_data(self):
        autor = Autor.objects.create(nombre="Autor Test", nacionalidad="Test")
        categoria = Categoria.objects.create(nombre="Cat Test")
        libro = Libro.objects.create(
            titulo="Libro Test",
            autor=autor,
            categoria=categoria,
            isbn="1234567890123",
            fecha_publicacion="2020-01-01",
            stock=5
        )
        return libro

    def test_actualizar_stock_positivo(self, setup_data):
        libro = setup_data
        LibroService.actualizar_stock(libro, 2)
        assert libro.stock == 7
        assert libro.disponible is True

    def test_actualizar_stock_negativo(self, setup_data):
        libro = setup_data
        LibroService.actualizar_stock(libro, -3)
        assert libro.stock == 2
        assert libro.disponible is True

    def test_actualizar_stock_agotar(self, setup_data):
        libro = setup_data
        LibroService.actualizar_stock(libro, -5)
        assert libro.stock == 0
        assert libro.disponible is False

    def test_actualizar_stock_error_insuficiente(self, setup_data):
        libro = setup_data
        with pytest.raises(ValidationError):
            LibroService.actualizar_stock(libro, -10)
