from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Libro, Autor, Categoria

class CategoriasAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.categoria = Categoria.objects.create(nombre='Ficción')

    def test_listar_categorias(self):
        url = reverse('categoria-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_crear_categoria(self):
        url = reverse('categoria-list')
        data = {"nombre": "Novela", "descripcion": "Categoría de novelas"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Categoria.objects.filter(nombre="Novela").exists())

    def test_update_categoria(self):
        url = reverse('categoria-detail', args=[self.categoria.id])
        data = {"nombre": "Ficción Actualizada", "descripcion": "Descripción actualizada"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, "Ficción Actualizada")

    def test_delete_categoria(self):
        url = reverse('categoria-detail', args=[self.categoria.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Categoria.objects.filter(id=self.categoria.id).exists())

class LibrosAPITest(APITestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Ficción')
        self.autor = Autor.objects.create(nombre='Autor Test', nacionalidad='Argentina')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.libro = Libro.objects.create(
            titulo='Libro Test',
            autor=self.autor,
            categoria=self.categoria,
            isbn='1234567890123',  # 13 dígitos
            fecha_publicacion='2020-01-01',
            descripcion='Descripción',
            stock=3
        )

    def test_listar_libros(self):
        url = reverse('libro-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_crear_libro(self):
        url = reverse('libro-list')
        data = {
            "titulo": "Nuevo Libro",
            "autor_id": self.autor.id,
            "categoria_id": self.categoria.id,
            "isbn": "0987654321123",
            "fecha_publicacion": "2020-01-01",
            "descripcion": "Otro libro",
            "stock": 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Libro.objects.filter(titulo="Nuevo Libro").exists())

    def test_crear_libro_isbn_invalido(self):
        url = reverse('libro-list')
        data = {
            "titulo": "Libro ISBN inválido",
            "autor_id": self.autor.id,
            "categoria_id": self.categoria.id,
            "isbn": "1234567890",  # Menos de 13 dígitos
            "fecha_publicacion": "2020-01-01",
            "descripcion": "ISBN incorrecto",
            "stock": 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Libro.objects.filter(titulo="Libro ISBN inválido").exists())

    def test_update_libro(self):
        url = reverse('libro-detail', args=[self.libro.id])
        data = {
            "titulo": "Libro Actualizado",
            "autor_id": self.autor.id,
            "categoria_id": self.categoria.id,
            "isbn": "1234567890123",
            "fecha_publicacion": "2020-01-01",
            "descripcion": "Descripción actualizada",
            "stock": 7
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.titulo, "Libro Actualizado")
        self.assertEqual(self.libro.stock, 7)

    def test_delete_libro(self):
        url = reverse('libro-detail', args=[self.libro.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Libro.objects.filter(id=self.libro.id).exists())
