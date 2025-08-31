from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apps.libros.models import Libro, Categoria
from apps.autores.models import Autor
from apps.prestamos.models import Prestamo
from datetime import date, timedelta

class PrestamosAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.autor = Autor.objects.create(nombre='Autor Prueba', nacionalidad='Argentina')
        self.categoria = Categoria.objects.create(nombre='Ficción')
        self.libro = Libro.objects.create(
            titulo='Libro Prueba',
            autor=self.autor,
            categoria=self.categoria,
            isbn='1234567890123',
            fecha_publicacion='2020-01-01',
            descripcion='Descripción',
            stock=5
        )
        self.client.login(username='testuser', password='testpass')
        # Crear un préstamo inicial
        self.prestamo = Prestamo.objects.create(
            usuario=self.user,
            libro=self.libro,
            fecha_devolucion_esperada=date.today() + timedelta(days=7)
        )

    def test_listar_prestamos(self):
        url = reverse('prestamo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_crear_prestamo(self):
        url = reverse('prestamo-list')
        data = {
            "libro_id": self.libro.id,
            "dias_prestamo": 7
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Prestamo.objects.filter(usuario=self.user, libro=self.libro).count() >= 2)

    def test_devolver_prestamo(self):
        url = reverse('prestamo-devolver', args=[self.prestamo.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302])
        self.prestamo.refresh_from_db()
        self.assertIsNotNone(self.prestamo.fecha_devolucion)

    def test_devolver_prestamo_con_fecha_vencida(self):
        # Simular que la fecha de devolución esperada ya pasó
        Prestamo.objects.filter(id=self.prestamo.id).update(
            fecha_devolucion_esperada=date.today() - timedelta(days=1)
        )

        url = reverse('prestamo-devolver', args=[self.prestamo.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302])
        self.prestamo.refresh_from_db()
        self.assertIsNotNone(self.prestamo.fecha_devolucion)

    def test_no_prestar_libro_no_disponible(self):
        
        self.libro.stock = 0
        self.libro.disponible = False
        self.libro.save()
        url = reverse('prestamo-list')
        data = {
            "libro_id": self.libro.id,
            "dias_prestamo": 7
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('libro', response.data)

    def test_historial_prestamos(self):
        
        self.prestamo.fecha_devolucion = date.today()
        self.prestamo.save()
        url = reverse('prestamo-historial')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        
        for item in response.data:
            self.assertIsNotNone(item['fecha_devolucion'])
