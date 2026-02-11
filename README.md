# 📚 Biblioteca Django DRF - Expert-Aligned

Sistema de gestión de biblioteca profesional desarrollado con **Django 5** y **Django REST Framework**. Este proyecto ha sido optimizado y alineado con estándares de ingeniería de software de alto nivel, incluyendo optimización de consultas, arquitectura de servicios y seguridad avanzada.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://biblioteca-django-drf.onrender.com)

## 🚀 Características Principales

### 💎 Excelencia Técnica (Expert Alignment)

- **Optimización de Consultas (N+1)**: Uso estratégico de `select_related` y `prefetch_related` para un rendimiento API superior.
- **Service Layer Architecture**: Lógica de negocio encapsulada en servicios (`LibroService`, `PrestamoService`), manteniendo las vistas delgadas y testeables.
- **Gestión de Errores Profesional**: Jerarquía de excepciones personalizada (`BibliotecaBaseError`) para respuestas API consistentes.
- **API Auto-Documentada**: Enriquecimiento exhaustivo de metadatos con `drf-spectacular` y `help_text`.
- **Throttling**: Protección integrada contra abuso de la API para usuarios anónimos y autenticados.

### 🛠️ Core Funcional

- **Gestión Completa**: Libros, Autores, Categorías, Préstamos y Usuarios.
- **Imágenes en la Nube**: Integración completa con **Cloudinary** para portadas y avatares.
- **Seguridad Pro**: Cabeceras de seguridad de producción (HSTS, Secure Cookies, Clickjacking protection).
- **Admin Premium**: Panel de administración personalizado y protegido.

## 🛠️ Tecnologías

- **Backend**: Django 5.2.1, DRF 3.16
- **Base de Datos**: MySQL (Clever Cloud / Local Docker)
- **Media**: Cloudinary
- **Servidor Web**: Gunicorn + WhiteNoise (Servicio de estáticos eficiente)
- **Infraestructura**: Docker, Docker Compose, Render

## 💻 Instalación Local

### Con Docker (Recomendado)

1. Clona el repositorio.
2. Crea un archivo `.env` basado en `.env.example` con tus credenciales.
3. Ejecuta:

   ```bash
   docker-compose up --build
   ```

4. Aplica las migraciones:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

### Sin Docker (Entorno Virtual)

1. Crea un venv: `python -m venv venv`
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura tus variables de entorno en un `.env`.
4. Ejecuta: `python manage.py migrate` y `python manage.py runserver`

## 🌍 Despliegue en Render

Este proyecto está pre-configurado para **Render.com** mediante Blueprint (`render.yaml`) y un script de construcción automatizado (`build.sh`).

1. Conecta tu repositorio a Render.
2. Render detectará automáticamente el archivo `render.yaml`.
3. Configura las variables de entorno en el Dashboard de Render (ver `.env.example`).
4. El despliegue ejecutará automáticamente migraciones y recolectará estáticos.

## 📖 Documentación de la API

La API está documentada dinámicamente utilizando estándares de **OpenAPI 3.0**:

- **Swagger UI**: `/api/docs/`
- **Redoc**: `/api/redoc/`
- **Schema**: `/api/schema/`

## 🔒 Seguridad

- Autenticación JWT y de Sesión.
- Protección contra fuerza bruta en el login.
- Cabeceras de seguridad estrictas activas en producción.
- Permisos granulares por objeto y acción.

---

Desarrollado con ❤️ por **Argenis Manzanares** — *Elevando el estándar de las aplicaciones Django.*
