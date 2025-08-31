from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, filters
from .models import Categoria, Libro
from apps.autores.models import Autor
from .serializers import CategoriaSerializer, LibroSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.prestamos.models import Prestamo
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q

@login_required
def inicio(request):
    """
    Vista de inicio que muestra un resumen de la biblioteca y las categorías con sus libros.
    """
    # Obtener estadísticas de libros
    total_libros = Libro.objects.count()
    libros_disponibles = Libro.objects.filter(disponible=True).count()

    # Obtener préstamos activos del usuario actual
    if request.user.is_authenticated:
        prestamos_activos = Prestamo.objects.filter(
            usuario=request.user,
            fecha_devolucion__isnull=True
        ).count()
    else:
        prestamos_activos = 0

    # Obtener categorías y sus libros
    from apps.libros.models import Categoria
    categorias = Categoria.objects.prefetch_related('libro_set').all()
    categorias_con_libros = []
    for categoria in categorias:
        libros = categoria.libro_set.all()
        categorias_con_libros.append({
            'categoria': categoria,
            'libros': libros
        })

    context = {
        'title': 'Inicio - Biblioteca',
        'total_libros': total_libros,
        'libros_disponibles': libros_disponibles,
        'prestamos_activos': prestamos_activos,
        'categorias_con_libros': categorias_con_libros,
    }
    return render(request, 'inicio.html', context)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['disponible', 'categoria', 'autor']
    search_fields = ['titulo', 'isbn', 'autor__nombre']
    ordering_fields = ['titulo', 'fecha_publicacion']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

@login_required
def lista_libros(request):

    # Obtener parámetros de búsqueda
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    
    # Filtrar libros
    libros = Libro.objects.all()
    
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__nombre__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    if categoria_id:
        libros = libros.filter(categoria_id=categoria_id)
    
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()
    
    context = {
        'libros': libros,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': int(categoria_id) if categoria_id else ''
    }
    return render(request, 'libros.html', context)

@login_required
def crear_libro(request):
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            form_data = request.POST.copy()
            imagen = request.FILES.get('imagen')
            
            # Crear el libro
            libro = Libro.objects.create(
                titulo=form_data['titulo'],
                autor_id=form_data['autor'],
                categoria_id=form_data['categoria'],
                isbn=form_data['isbn'],
                descripcion=form_data.get('descripcion', ''),
                fecha_publicacion=form_data['fecha_publicacion'],
                stock=form_data.get('stock', 1)
            )
            
            # Si hay una imagen, guardarla
            if imagen:
                libro.imagen = imagen
                libro.save()
                
            messages.success(request, 'Libro creado exitosamente.')
            return redirect('lista_libros')
        except ValidationError as e:
            messages.error(request, str(e))
    
    # Obtener autores y categorías para el formulario
    autores = Autor.objects.all()
    categorias = Categoria.objects.all()
    
    return render(request, 'crear_libro.html', {
        'autores': autores,
        'categorias': categorias
    })

@login_required
def prestar_libro(request, libro_id):
    try:
        libro = Libro.objects.get(id=libro_id)
        if libro.disponible:
            dias = int(request.POST.get('dias_prestamo', 7))
            Prestamo.objects.create(
                usuario=request.user,
                libro=libro,
                fecha_devolucion_esperada=timezone.now().date() + timezone.timedelta(days=dias)
            )
            messages.success(request, 'Libro prestado exitosamente.')
        else:
            messages.error(request, 'El libro no está disponible.')
    except (Libro.DoesNotExist, ValidationError, Exception) as e:
        messages.error(request, str(e))
    return redirect('lista_libros')

@login_required
def mis_prestamos(request):
    prestamos_activos = Prestamo.objects.filter(
        usuario=request.user,
        fecha_devolucion__isnull=True
    ).select_related('libro')
    
    prestamos_devueltos = Prestamo.objects.filter(
        usuario=request.user,
        fecha_devolucion__isnull=False
    ).select_related('libro').order_by('-fecha_devolucion')
    
    return render(request, 'prestamos.html', {
        'prestamos_activos': prestamos_activos,
        'prestamos_devueltos': prestamos_devueltos
    })

@login_required
def devolver_libro(request, prestamo_id):
    try:
        prestamo = Prestamo.objects.get(id=prestamo_id, usuario=request.user)
        if prestamo.fecha_devolucion:
            messages.warning(request, 'Este libro ya ha sido devuelto.')
        else:
            prestamo.fecha_devolucion = timezone.now().date()
            prestamo.save()
            
            # Marcar el libro como disponible
            libro = prestamo.libro
            libro.disponible = True
            libro.save()
            
            messages.success(request, 'Libro devuelto exitosamente.')
    except Prestamo.DoesNotExist:
        messages.error(request, 'Préstamo no encontrado.')
    
    return redirect('lista_prestamos')