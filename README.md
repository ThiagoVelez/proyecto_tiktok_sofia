# 📱 Proyecto TikTok (Backend - Proyecto Sofía)

Backend robusto, modular y de alto rendimiento para una plataforma de videos cortos estilo **TikTok**, desarrollado con **FastAPI**, **SQLAlchemy** y **MySQL 8**. Diseñado bajo principios **SOLID** y una arquitectura desacoplada por microservicios.

---

## 🚀 Características Principales

### 1. 🎥 Carga y Streaming de Videos (Estilo TikTok)
- **Subida Directa Multipart (`POST /api/v1/videos/publish`):** Permite subir video binario, miniatura opcional, metadatos, tags y configuración de privacidad en una sola petición.
- **Streaming con HTTP 206 Partial Content:** Soporte completo de cabecera `Range: bytes=start-end` (RFC 7233) para reproducción instantánea sin descargar el archivo completo, soporte de rebobinado/salto rápido (`seek`) y prebuffering continuo.
- **Soporte de peticiones `HEAD`:** Inspección de cabeceras de medios (`Accept-Ranges`, `Content-Length`) antes de la reproducción.
- **Extracción Automática de Hashtags:** Detecta hashtags enviados en el formulario y extrae automáticamente los `#hashtags` del título o descripción.

### 2. ⏳ Microservicio de Historias de 24 Horas (Stories)
- **Contenido Efímero:** Publicación de fotos y videos verticales con fecha de caducidad automática de 24 horas (`expires_at`).
- **Story Tray (`GET /api/v1/stories/feed`):** Bandeja superior de historias agrupadas por creador con avatar, indicador de contenido no visto (`has_unseen`) y ordenamiento inteligente.
- **Telemetría y Lista de Espectadores:** Registro de vistas únicas y consulta de espectadores (`GET /api/v1/stories/{id}/viewers`) protegido por RBAC (solo creador o moderador).

### 3. 🛡️ Motor de Reglas de Negocio en Tiempo Real (`backend/reglas/`)
- **Control Parental:** Límites de tiempo diario en pantalla, toque de queda nocturno (bloqueo automático entre horas configuradas) y vinculación familiar padre-hijo con PIN criptográfico.
- **Protección de Audiencia:** Clasificación automática de videos (`all_ages`, `teen`, `mature`, `restricted`).
- **Seguridad y Moderación Heurística:** Detección de lenguaje inapropiado, palabras ofensivas y evasión de filtros mediante *leetspeak* (ej: `p0rn0`, `m4t4r`).

### 4. ❤️ Interacciones y Red Social
- **Likes:** Videos y comentarios con actualización atómica de contadores.
- **Comentarios:** Árbol de comentarios y respuestas anidadas con filtro de toxicidad.
- **Compartir (Share):** Registro de métricas para WhatsApp, Facebook, Instagram, Twitter y copia de enlace.
- **Favoritos (Bookmarks):** Guardado de videos en colecciones personales.
- **Buscador Integral (`/api/v1/search`):** Búsqueda combinada de videos, creadores, hashtags en tendencia y catálogo de pistas de sonido.

---

## 🏗️ Arquitectura del Sistema

```
proyecto_sofia/
├── backend/
│   ├── core/                  # Configuración, base de datos ORM, seguridad JWT y respuestas
│   ├── microservices/
│   │   ├── auth_service/      # Registro, login, refresh tokens, sesiones
│   │   ├── user_service/      # Perfiles, follow/unfollow, vinculación parental
│   │   ├── video_service/     # Publicación, feeds Para Ti / Siguiendo, streaming Range
│   │   ├── story_service/     # Historias de 24 horas, feed tray, visualizaciones
│   │   ├── interaction_service/# Likes, comentarios, respuestas, shares, bookmarks
│   │   ├── moderation_service/# Auditoría de moderación, reportes y RBAC
│   │   ├── notification_service/# Notificaciones en tiempo real
│   │   └── search_service/    # Motor de búsqueda, hashtags en tendencia y sonidos
│   ├── reglas/                # Motor unificado de reglas de negocio y seguridad
│   ├── sql/                   # Script DDL schema.sql (21 tablas MySQL 8)
│   ├── tests/                 # Suite de pruebas automatizadas
│   ├── uploads/               # Directorio local de almacenamiento multimedia
│   ├── main.py                # API Gateway y orquestador FastAPI
│   └── seed_data.py           # Generador de datos semilla
├── frontend/                  # Espacio reservado para la interfaz gráfica
└── .gitignore
```

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.12+ / 3.14
- **Framework API:** FastAPI / Starlette
- **ORM & BD:** SQLAlchemy 2.0+ / MySQL 8.0+ (PyMySQL) / SQLite (tests en memoria)
- **Seguridad:** Cifrado nativo con `bcrypt`, Tokens JWT (`PyJWT`), Roles RBAC (`admin`, `moderator`, `creator`, `user`, `minor`, `parent`)
- **Servidor ASGI:** Uvicorn

---

## 📦 Instalación y Puesta en Marcha

### 1. Clonar el Repositorio
```bash
git clone https://github.com/ThiagoVelez/proyecto_tiktok.git
cd proyecto_tiktok
```

### 2. Configurar Entorno Virtual e Instalar Dependencias
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Configurar Base de Datos MySQL
1. Crea la base de datos en tu servidor MySQL:
   ```sql
   CREATE DATABASE proyecto_sofia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Ejecuta el script DDL [`backend/sql/schema.sql`](backend/sql/schema.sql) o permite que SQLAlchemy cree las tablas automáticamente.
3. Copia el archivo de variables de entorno y ajusta tus credenciales:
   ```bash
   cp backend/.env.example backend/.env
   ```

### 4. Cargar Datos Semilla (Opcional)
Pobla la base de datos con cuentas de prueba (`admin`, creadores, menor con control parental), videos, tendencias y sonidos:
```bash
python backend/seed_data.py
```

### 5. Iniciar el Servidor de Desarrollo
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- **Documentación Interactiva (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Pruebas Automatizadas

Ejecuta la suite integral de pruebas para validar reglas de seguridad, control parental, interacciones, publicaciones directas y ciclo de vida de historias:
```bash
python backend/tests/test_rules_and_backend.py
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
