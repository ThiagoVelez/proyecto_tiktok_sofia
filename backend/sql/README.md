# Base de Datos MySQL - Proyecto Sofía (TikTok Backend)

Este directorio contiene el script DDL para inicializar la base de datos `proyecto_sofia` en MySQL.

> **Importante**: Cumpliendo con los requerimientos, el script `schema.sql` contiene **exclusivamente la estructura de tablas, tipos de datos, índices, llaves primarias, foráneas y restricciones**. No contiene ningún registro semilla (seed) ni datos de prueba (`INSERT`).

---

## 📋 Estructura de Tablas Creadas

1. **`users`**: Cuentas de usuario, credenciales cifradas, roles (`user`, `creator`, `moderator`, `admin`), tipo de cuenta (`standard`, `minor`, `parent`), estado de verificación y privacidad.
2. **`parental_controls`**: Configuración de control parental por usuario (código PIN cifrado, bloqueo por intentos, límite diario de minutos de pantalla, toque de queda nocturno, modo restringido).
3. **`parent_child_links`**: Vinculación de cuentas entre padre/tutor legal y cuenta de menor de edad.
4. **`screen_time_sessions`**: Registro y cálculo de minutos consumidos por día por menores de edad.
5. **`sounds`**: Catálogo de audios y canciones originales o licenciadas utilizadas en los videos cortos.
6. **`videos`**: Publicaciones de video vertical con métricas (vistas, likes, comentarios, compartidos, guardados), visibilidad, clasificación de audiencia y estado de moderación.
7. **`hashtags`**: Registro de etiquetas en tendencia y conteo de popularidad.
8. **`video_hashtags`**: Relación n:m entre videos y hashtags.
9. **`video_likes`**: Registro único de 'Me Gusta' por usuario y video.
10. **`comments`**: Comentarios en videos con soporte para respuestas en hilos (`parent_comment_id`).
11. **`comment_likes`**: Reacciones a comentarios.
12. **`follows`**: Relaciones de seguidores y seguidos con soporte para cuentas privadas.
13. **`saved_videos`**: Videos marcados como favoritos / guardados en colecciones.
14. **`video_shares`**: Conteo analítico de compartidos por red social/enlace.
15. **`video_views`**: Telemetría de retención y tiempo de reproducción por video.
16. **`content_reports`**: Denuncias de la comunidad categorizadas por tipo de infracción.
17. **`moderation_audits`**: Registro histórico de acciones tomadas por el módulo de reglas automáticas.
18. **`notifications`**: Alertas en tiempo real a usuarios y notificaciones parentales a tutores.
19. **`auth_sessions`**: Tokens de refresco (JWT) y sesiones activas.

---

## 🚀 Cómo ejecutar el Script en MySQL Workbench

1. Abre **MySQL Workbench** (como se muestra en tu conexión configurada a `127.0.0.1:3306` con usuario `root`).
2. Conéctate a la instancia local.
3. Ve al menú superior: **File -> Open SQL Script...** (o presiona `Ctrl + Shift + O`).
4. Selecciona el archivo:
   `c:\Users\VICTUS\Desktop\proyecto_sofia\backend\sql\schema.sql`
5. Presiona el botón del rayo ⚡ (**Execute**) o `Ctrl + Shift + Enter`.
6. En el panel de la izquierda ("Schemas"), haz clic derecho y selecciona **Refresh All**. Verás el esquema `proyecto_sofia` con todas sus tablas creadas.
