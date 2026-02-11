import pytest
from apps.common.exceptions import BusinessLogicError
from django.contrib.auth.models import User
from apps.libros.models import Libro, Categoria
from apps.autores.models import Autor
from apps.prestamos.models import Prestamo, MAX_LIBROS_POR_USUARIO
from apps.prestamos.services import PrestamoService
from datetime import date

@pytest.mark.django_db
class TestPrestamoService:
    @pytest.fixture
    def setup_base_data(self):
        user = User.objects.create_user(username="testuser", password="pass")
        autor = Autor.objects.create(nombre="Autor Test", nacionalidad="Test")
        categoria = Categoria.objects.create(nombre="Cat Test")
        libro = Libro.objects.create(
            titulo="Libro Test",
            autor=autor,
            categoria=categoria,
            isbn="1234567890123",
            fecha_publicacion="2020-01-01",
            stock=1
        )
        return user, libro

    def test_crear_prestamo_exitoso(self, setup_base_data):
        user, libro = setup_base_data
        prestamo = PrestamoService.crear_prestamo(user, libro)
        
        assert prestamo.usuario == user
        assert prestamo.libro == libro
        assert prestamo.fecha_devolucion is None
        
        libro.refresh_from_db()
        assert libro.stock == 0
        assert libro.disponible is False

    def test_crear_prestamo_sin_stock(self, setup_base_data):
        user, libro = setup_base_data
        libro.stock = 0
        libro.disponible = False
        libro.save()
        
        with pytest.raises(BusinessLogicError) as exc:
            PrestamoService.crear_prestamo(user, libro)
        assert 'disponible' in str(exc.value)

    def test_crear_prestamo_limite_alcanzado(self, setup_base_data):
        user, libro = setup_base_data
        # Crear libros extra para el test
        for i in range(MAX_LIBROS_POR_USUARIO):
            l = Libro.objects.create(
                titulo=f"Libro {i}", autor=libro.autor, isbn=f"111111111111{i}",
                fecha_publicacion="2020-01-01", stock=1
            )
            PrestamoService.crear_prestamo(user, l)
            
        with pytest.raises(BusinessLogicError) as exc:
            PrestamoService.crear_prestamo(user, libro)
        assert 'límite' in str(exc.value)

    def test_devolver_libro_exitoso(self, setup_base_data):
        user, libro = setup_base_data
        prestamo = PrestamoService.crear_prestamo(user, libro)
        
        PrestamoService.devolver_libro(prestamo)
        
        prestamo.refresh_from_db()
        assert prestamo.devuelto is True
        
        libro.refresh_from_db()
        assert libro.stock == 1
        assert libro.disponible is True
