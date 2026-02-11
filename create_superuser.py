#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente en producción.
Solo se ejecuta si no existe ningún superusuario.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar si ya existe un superusuario
if not User.objects.filter(is_superuser=True).exists():
    # Obtener credenciales de variables de entorno
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@biblioteca.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    
    if password:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ Superusuario "{username}" creado exitosamente.')
    else:
        print('⚠️ No se encontró DJANGO_SUPERUSER_PASSWORD en las variables de entorno.')
        print('   Configura esta variable en Render para crear el superusuario automáticamente.')
else:
    print('ℹ️ Ya existe un superusuario. No se creó uno nuevo.')
