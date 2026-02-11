"""
URL configuration for biblioteca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.libros import views as libros_views
from apps.prestamos import views as prestamos_views
from apps.autores.views import AutorViewSet
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'libros', libros_views.LibroViewSet)
router.register(r'categorias', libros_views.CategoriaViewSet, basename='categoria')
router.register(r'autores', AutorViewSet, basename='autor')
router.register(r'prestamos', prestamos_views.PrestamoViewSet, basename='prestamo')

# Cambiar el título del admin
admin.site.site_header = 'Panel de Administración - Biblioteca'
admin.site.site_title = 'Biblioteca Admin'
admin.site.index_title = 'Gestión de Biblioteca'

urlpatterns = [
    # Redirección para compatibilidad con /login/
    path('login/', lambda request: redirect('usuarios:login')),
    # URL del admin con un nombre menos predecible
    path('gestor-biblioteca/', admin.site.urls),
    
    # Incluir las URLs de la aplicación de usuarios solo una vez
    path('usuarios/', include('apps.usuarios.urls')),
    
    # URLs de la API
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/autores/', include('apps.autores.urls')),  # Eliminado por redundancia
    path('api-auth/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # URLs de la aplicación de usuarios

    # URLs de la aplicación principal
    path('', libros_views.inicio, name='inicio'),
    path('libros/', libros_views.lista_libros, name='lista_libros'),
    path('prestamos/', prestamos_views.lista_prestamos, name='lista_prestamos'),
    path('prestamos/crear/', prestamos_views.crear_prestamo, name='crear_prestamo'),
    path('prestamos/devolver/<int:prestamo_id>/', prestamos_views.devolver_libro, name='devolver_libro'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
