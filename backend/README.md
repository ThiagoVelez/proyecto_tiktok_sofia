# Proyecto Sofía - Backend (Plataforma Estilo TikTok)

Backend modular, escalable y robusto desarrollado con **Python (FastAPI)**, siguiendo principios **SOLID** y diseñado con una arquitectura distribuida lista para **Microservicios**.

Incluye un motor centralizado de **Reglas de Negocio, Control Parental y Protección de Audiencia** en la carpeta `backend/reglas/`, además del script DDL estricto en `backend/sql/schema.sql` para MySQL.

---

##  Arquitectura del Sistema

```
proyecto_sofia/
├── backend/
│   ├── sql/                                # Definición DDL de base de datos MySQL (0 datos semilla)
│   │   ├── schema.sql                      # Script SQL con las 19 tablas, índices y restricciones
│   │   └── README.md                       # Instrucciones para MySQL Workbench
│   │
│   ├── reglas/                             # CARPETA REQUERIDA: Reglas de negocio y protección
│   │   ├── __init__.py                     # Exportación unificada del paquete
│   │   ├── config_rules.json               # Configuración de categorías de riesgo, patrones y límites
│   │   ├── parental_control.py             # Código PIN, tiempo diario, toque de queda y control de DMs
│   │   ├── content_safety.py               # Detección de groserías, acoso, leetspeak y enmascaramiento
│   │   ├── audience_protection.py          # Clasificador por edades (All Ages, Teen, Mature, Restricted)
│   │   └── rule_evaluator.py               # Fachada central (Facade) que orquesta las reglas
│   │
│   ├── microservices/                      # Microservicios desacoplados
│   │   ├── auth_service/                   # Autenticación, registro, JWT y detección de edad
│   │   ├── user_service/                   # Perfiles, seguimiento y configuración parental
│   │   ├── video_service/                  # Publicación, feeds 'Para Ti' y 'Siguiendo', métricas
│   │   ├── interaction_service/            # Likes, comentarios moderados, favoritos y shares
│   │   ├── moderation_service/             # Denuncias de la comunidad y auditorías
│   │   └── notification_service/           # Alertas de actividad y notificaciones push a padres
│   │
│   ├── core/                               # Infraestructura compartida (SOLID / Inversión de Control)
│   │   ├── config.py                       # Variables de entorno (.env)
│   │   ├── database.py                     # Conexión SQLAlchemy y modelos ORM
│   │   ├── security.py                     # Criptografía Bcrypt y manejo de JWT
│   │   ├── response.py                     # Envelope estandarizado de respuesta API
│   │   └── exceptions.py                   # Excepciones de dominio y restricciones parentales
│   │
│   ├── tests/                              # Pruebas automatizadas del motor de reglas y API
│   │   └── test_rules_and_backend.py
│   │
│   ├── uploads/                            # Directorio local para almacenamiento multimedia
│   ├── main.py                             # API Gateway y orquestador FastAPI
│   ├── requirements.txt                    # Dependencias del proyecto
│   ├── .env.example                        # Plantilla de variables de entorno
│   └── .env                                # Configuración activa
```

---

##  Módulo `reglas/`: Control Parental y Protección de Audiencia

Tal como solicitaste, la carpeta `backend/reglas/` contiene el motor que garantiza que la plataforma sea apta para todo público y proteja la experiencia de la audiencia:

1. **Código PIN Parental (`parental_control.py`)**:
   - Cifrado de alta seguridad `PBKDF2-HMAC-SHA256` con sal única para el código PIN de 4 a 6 dígitos.
   - Bloqueo temporal por intentos fallidos (3 intentos fallidos bloquean el acceso por 15 minutos).
   - Verificación estricta de tiempo de descanso nocturno (**Toque de Queda / Curfew**) por ejemplo de 22:00 a 06:00.
   - Límite diario de tiempo de pantalla (ej. 120 minutos configurables).

2. **Seguridad y Moderación de Contenido (`content_safety.py`)**:
   - Motor heurístico anti-evasión que normaliza textos y detecta técnicas como **Leetspeak** (ej. `p0rn0` -> `porno`, `m4t4r` -> `matar`).
   - Categorías evaluadas: violencia, contenido sexual explícito, discurso de odio, ciberacoso/bullying, autolesión, estafas/spam y lenguaje soez.
   - **Enmascaramiento automático de comentarios**: las groserías o palabras fuertes son censuradas automáticamente con asteriscos (ej: `i*****` y `m*****`).

3. **Clasificación de Audiencia (`audience_protection.py`)**:
   - Clasifica los videos en 4 categorías:
     - `all_ages`: Apto para niños, familias y todo público.
     - `teen`: Apto para mayores de 13 años.
     - `mature`: Mayores de 18 años (humor adulto, no explícito).
     - `restricted`: Contenido con advertencia estricta, bloqueado bajo Modo Restringido.
   - Si un video contiene violencia extrema o pornografía, es **rechazado inmediatamente (`banned`)** o retenido en revisión (`under_review`).

4. **Filtrado del Feed 'Para Ti'**:
   - Si un menor o un usuario con **Modo Restringido** navega por la plataforma, el sistema **excluye automáticamente** los videos que no sean `all_ages`.
   - Si se supera el límite de tiempo o está en horario de descanso, el feed se bloquea con aviso informativo.

---

##  Base de Datos MySQL (`sql/schema.sql`)

El archivo [schema.sql](file:///c:/Users/VICTUS/Desktop/proyecto_sofia/backend/sql/schema.sql) contiene **19 tablas normalizadas**:
- `users`: Cuentas, roles (`user`, `creator`, `moderator`, `admin`), y tipo (`standard`, `minor`, `parent`).
- `parental_controls`: Estado del control parental, hash del PIN, límites de minutos diarios, horario de descanso.
- `parent_child_links`: Enlace entre cuenta del tutor/padre y la cuenta del menor.
- `screen_time_sessions`: Monitoreo diario de minutos consumidos por usuario.
- `sounds`: Catálogo de pistas de audio / canciones.
- `videos`: Videos verticales con contador de métricas, rating de audiencia y estado de moderación.
- `hashtags` y `video_hashtags`: Etiquetas y relaciones N a M.
- `video_likes`: Me gusta en videos.
- `comments` y `comment_likes`: Comentarios con soporte para hilos jerárquicos y likes.
- `follows`: Seguidores y seguidos con soporte de cuentas privadas.
- `saved_videos`: Favoritos / Guardados.
- `video_shares`: Métricas de compartición (WhatsApp, Instagram, etc.).
- `video_views`: Telemetría de reproducción.
- `content_reports`: Denuncias de la comunidad.
- `moderation_audits`: Registro de auditoría del motor de reglas automáticas.
- `notifications`: Notificaciones a usuarios y alertas push a padres.
- `auth_sessions`: Sesiones activas y tokens de refresco.

**Sin datos semilla**: No contiene sentencias `INSERT` para que inicies con una base de datos limpia.

---

##  Cómo Ejecutar el Proyecto

### 1. Cargar la Base de Datos en MySQL Workbench
1. Abre tu **MySQL Workbench** conectado a `127.0.0.1:3306` (usuario `root`).
2. Abre el archivo: `backend/sql/schema.sql`.
3. Ejecuta el script completo (icono del rayo ⚡).
4. Se creará la base de datos `proyecto_sofia` con todas sus tablas e índices.

### 2. Configurar el archivo `.env`
Edita `backend/.env` si tu MySQL tiene contraseña:
```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui
DB_NAME=proyecto_sofia
```

### 3. Iniciar el Servidor Backend
En una terminal PowerShell en la raíz del proyecto:
```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Documentación Interactiva Swagger
Una vez iniciado el servidor, ingresa en tu navegador a:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Podrás probar todos los endpoints directamente desde la interfaz web.
