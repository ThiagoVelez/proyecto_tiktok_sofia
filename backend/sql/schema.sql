-- =============================================================================
-- PROYECTO SOFÍA - PLATAFORMA DE VIDEOS CORTOS (ESTILO TIKTOK)
-- SCRIPT DDL: Estructura Completa de Base de Datos MySQL
-- =============================================================================
-- NOTA: Este archivo contiene EXCLUSIVAMENTE la definición de tablas, relaciones,
-- índices y restricciones de integridad. NO CONTIENE DATOS SEMILLA NI INSERTS.
-- Compatible al 100% con MySQL 8.0+ (sin advertencias de tipo o deprecated widths).
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `proyecto_sofia`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `proyecto_sofia`;

-- Desactivar temporalmente verificación de llaves foráneas para orden de creación
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- 1. TABLA: users (Usuarios principales de la plataforma)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `phone_number` VARCHAR(25) NULL DEFAULT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `bio` VARCHAR(250) NULL DEFAULT NULL,
  `avatar_url` VARCHAR(500) NULL DEFAULT NULL,
  `birth_date` DATE NOT NULL,
  `role` ENUM('user', 'creator', 'moderator', 'admin') NOT NULL DEFAULT 'user',
  `account_type` ENUM('standard', 'minor', 'parent') NOT NULL DEFAULT 'standard',
  `is_verified` BOOLEAN NOT NULL DEFAULT FALSE,
  `is_private` BOOLEAN NOT NULL DEFAULT FALSE,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_username` (`username`),
  UNIQUE KEY `uk_users_email` (`email`),
  KEY `idx_users_birth_date` (`birth_date`),
  KEY `idx_users_role` (`role`),
  KEY `idx_users_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. TABLA: parental_controls (Configuración y Código de Control Parental)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `parental_controls`;
CREATE TABLE `parental_controls` (
  `user_id` BIGINT UNSIGNED NOT NULL,
  `is_enabled` BOOLEAN NOT NULL DEFAULT FALSE,
  `pin_hash` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Código PIN parental de 4-6 dígitos encriptado',
  `pin_failed_attempts` INT NOT NULL DEFAULT 0,
  `pin_locked_until` DATETIME NULL DEFAULT NULL,
  `daily_screen_time_limit_minutes` INT NOT NULL DEFAULT 120 COMMENT 'Límite de uso diario (minutos)',
  `curfew_start_time` TIME NULL DEFAULT '22:00:00' COMMENT 'Hora de bloqueo nocturno',
  `curfew_end_time` TIME NULL DEFAULT '06:00:00' COMMENT 'Hora de desbloqueo matutino',
  `restricted_mode` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Filtra contenido maduro para menores',
  `block_direct_messages` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Impide mensajes de desconocidos',
  `filter_mature_comments` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Oculta comentarios sensibles',
  `allow_search` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Control de uso del motor de búsqueda',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_parental_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. TABLA: parent_child_links (Vinculación entre cuenta de padre/tutor e hijo)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `parent_child_links`;
CREATE TABLE `parent_child_links` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `parent_user_id` BIGINT UNSIGNED NOT NULL,
  `child_user_id` BIGINT UNSIGNED NOT NULL,
  `pairing_code` VARCHAR(20) NULL DEFAULT NULL,
  `status` ENUM('pending', 'active', 'revoked') NOT NULL DEFAULT 'pending',
  `linked_at` DATETIME NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_parent_child` (`parent_user_id`, `child_user_id`),
  KEY `idx_child_user` (`child_user_id`),
  CONSTRAINT `fk_link_parent` FOREIGN KEY (`parent_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_link_child` FOREIGN KEY (`child_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. TABLA: screen_time_sessions (Monitoreo de tiempo en pantalla diario)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `screen_time_sessions`;
CREATE TABLE `screen_time_sessions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `session_date` DATE NOT NULL,
  `minutes_consumed` INT NOT NULL DEFAULT 0,
  `last_active_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_date_session` (`user_id`, `session_date`),
  CONSTRAINT `fk_screen_time_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. TABLA: sounds (Pistas de audio y música para los videos cortos)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `sounds`;
CREATE TABLE `sounds` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(150) NOT NULL,
  `artist_name` VARCHAR(100) NOT NULL DEFAULT 'Sonido Original',
  `audio_url` VARCHAR(500) NOT NULL,
  `cover_url` VARCHAR(500) NULL DEFAULT NULL,
  `duration_seconds` INT NOT NULL DEFAULT 60,
  `is_original` BOOLEAN NOT NULL DEFAULT TRUE,
  `author_user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `usage_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sounds_author` (`author_user_id`),
  KEY `idx_sounds_usage` (`usage_count` DESC),
  CONSTRAINT `fk_sounds_author` FOREIGN KEY (`author_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. TABLA: videos (Publicaciones de video tipo TikTok)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `videos`;
CREATE TABLE `videos` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `sound_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `title` VARCHAR(150) NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  `video_url` VARCHAR(500) NOT NULL,
  `thumbnail_url` VARCHAR(500) NOT NULL,
  `duration_seconds` DECIMAL(6,2) NOT NULL DEFAULT 15.00,
  `aspect_ratio` VARCHAR(10) NOT NULL DEFAULT '9:16',
  `views_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `likes_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `comments_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `shares_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `saves_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `visibility` ENUM('public', 'friends', 'private') NOT NULL DEFAULT 'public',
  `allow_comments` BOOLEAN NOT NULL DEFAULT TRUE,
  `allow_duet` BOOLEAN NOT NULL DEFAULT TRUE,
  `allow_stitch` BOOLEAN NOT NULL DEFAULT TRUE,
  `allow_download` BOOLEAN NOT NULL DEFAULT TRUE,
  `audience_rating` ENUM('all_ages', 'teen', 'mature', 'restricted') NOT NULL DEFAULT 'all_ages',
  `moderation_status` ENUM('approved', 'under_review', 'flagged', 'hidden', 'banned') NOT NULL DEFAULT 'approved',
  `moderation_reason` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_videos_user` (`user_id`),
  KEY `idx_videos_sound` (`sound_id`),
  KEY `idx_videos_feed` (`visibility`, `moderation_status`, `created_at` DESC),
  KEY `idx_videos_audience` (`audience_rating`, `moderation_status`),
  CONSTRAINT `fk_videos_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_videos_sound` FOREIGN KEY (`sound_id`) REFERENCES `sounds` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 7. TABLA: hashtags (Etiquetas para categorización y tendencias)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `hashtags`;
CREATE TABLE `hashtags` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tag` VARCHAR(100) NOT NULL,
  `videos_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `views_count` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `is_banned` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_hashtags_tag` (`tag`),
  KEY `idx_hashtags_popularity` (`videos_count` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 8. TABLA: video_hashtags (Relación Muchos a Muchos: Videos y Hashtags)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `video_hashtags`;
CREATE TABLE `video_hashtags` (
  `video_id` BIGINT UNSIGNED NOT NULL,
  `hashtag_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`video_id`, `hashtag_id`),
  KEY `idx_vh_hashtag` (`hashtag_id`),
  CONSTRAINT `fk_vh_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_vh_hashtag` FOREIGN KEY (`hashtag_id`) REFERENCES `hashtags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 9. TABLA: video_likes (Interacción 'Me Gusta' en Videos)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `video_likes`;
CREATE TABLE `video_likes` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `video_id` BIGINT UNSIGNED NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_video_like` (`user_id`, `video_id`),
  KEY `idx_vl_video` (`video_id`),
  CONSTRAINT `fk_vl_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_vl_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 10. TABLA: comments (Comentarios en Videos con Soporte para Hilos Anidados)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `video_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `parent_comment_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID de comentario padre si es respuesta',
  `content` VARCHAR(1000) NOT NULL,
  `likes_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `is_flagged` BOOLEAN NOT NULL DEFAULT FALSE,
  `moderation_status` ENUM('approved', 'flagged', 'hidden', 'banned') NOT NULL DEFAULT 'approved',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_comments_video` (`video_id`, `created_at` DESC),
  KEY `idx_comments_user` (`user_id`),
  KEY `idx_comments_parent` (`parent_comment_id`),
  CONSTRAINT `fk_comm_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_comm_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_comm_parent` FOREIGN KEY (`parent_comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 11. TABLA: comment_likes (Reacciones a Comentarios)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `comment_likes`;
CREATE TABLE `comment_likes` (
  `user_id` BIGINT UNSIGNED NOT NULL,
  `comment_id` BIGINT UNSIGNED NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `comment_id`),
  KEY `idx_cl_comment` (`comment_id`),
  CONSTRAINT `fk_cl_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cl_comment` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 12. TABLA: follows (Relación Seguidor / Siguiendo)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `follows`;
CREATE TABLE `follows` (
  `follower_id` BIGINT UNSIGNED NOT NULL,
  `following_id` BIGINT UNSIGNED NOT NULL,
  `status` ENUM('active', 'pending') NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`follower_id`, `following_id`),
  KEY `idx_follows_following` (`following_id`),
  CONSTRAINT `fk_follows_follower` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_follows_following` FOREIGN KEY (`following_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 13. TABLA: saved_videos (Videos Guardados / Favoritos)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `saved_videos`;
CREATE TABLE `saved_videos` (
  `user_id` BIGINT UNSIGNED NOT NULL,
  `video_id` BIGINT UNSIGNED NOT NULL,
  `collection_name` VARCHAR(50) NOT NULL DEFAULT 'Favoritos',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `video_id`),
  KEY `idx_saved_video` (`video_id`),
  CONSTRAINT `fk_sv_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sv_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 14. TABLA: video_shares (Métricas de Compartidos por Plataforma)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `video_shares`;
CREATE TABLE `video_shares` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `video_id` BIGINT UNSIGNED NOT NULL,
  `share_platform` ENUM('whatsapp', 'facebook', 'instagram', 'twitter', 'link_copy', 'other') NOT NULL DEFAULT 'link_copy',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_shares_video` (`video_id`),
  CONSTRAINT `fk_shares_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_shares_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 15. TABLA: video_views (Registro Analítico de Reproducciones)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `video_views`;
CREATE TABLE `video_views` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `video_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `watch_duration_seconds` DECIMAL(6,2) NOT NULL DEFAULT 0.00,
  `watched_full` BOOLEAN NOT NULL DEFAULT FALSE,
  `ip_address` VARCHAR(45) NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_views_video` (`video_id`),
  KEY `idx_views_created_at` (`created_at`),
  CONSTRAINT `fk_views_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_views_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 16. TABLA: content_reports (Reportes de la Comunidad sobre Videos o Comentarios)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `content_reports`;
CREATE TABLE `content_reports` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `reporter_user_id` BIGINT UNSIGNED NOT NULL,
  `target_type` ENUM('video', 'comment', 'user') NOT NULL,
  `target_id` BIGINT UNSIGNED NOT NULL,
  `reason_category` ENUM(
    'inappropriate_for_minors',
    'violence_graphic',
    'hate_speech',
    'harassment_bullying',
    'sexual_content',
    'spam_scam',
    'self_harm',
    'copyright_violation',
    'other'
  ) NOT NULL,
  `details` TEXT NULL DEFAULT NULL,
  `status` ENUM('pending', 'under_review', 'resolved_action_taken', 'dismissed') NOT NULL DEFAULT 'pending',
  `moderator_notes` TEXT NULL DEFAULT NULL,
  `resolved_by_user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `resolved_at` DATETIME NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_reports_target` (`target_type`, `target_id`),
  KEY `idx_reports_status` (`status`),
  CONSTRAINT `fk_reports_reporter` FOREIGN KEY (`reporter_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_reports_resolver` FOREIGN KEY (`resolved_by_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 17. TABLA: moderation_audits (Auditoría del Motor de Reglas y Moderación)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `moderation_audits`;
CREATE TABLE `moderation_audits` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `target_type` ENUM('video', 'comment', 'user_profile', 'search_query') NOT NULL,
  `target_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `rule_triggered` VARCHAR(100) NOT NULL COMMENT 'Identificador de regla activada del módulo reglas',
  `severity_level` ENUM('low', 'medium', 'high', 'critical') NOT NULL,
  `action_applied` ENUM('none', 'content_flagged', 'age_restricted', 'auto_hidden', 'auto_banned', 'queued_review') NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `evaluated_text_snippet` VARCHAR(500) NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_mod_audits_target` (`target_type`, `target_id`),
  KEY `idx_mod_audits_rule` (`rule_triggered`),
  KEY `idx_mod_audits_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 18. TABLA: notifications (Notificaciones a Usuarios y Alertas Parentales)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `sender_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `type` ENUM(
    'new_like',
    'new_comment',
    'new_follower',
    'mention',
    'parental_curfew_alert',
    'parental_limit_exceeded',
    'moderation_warning',
    'system_announcement'
  ) NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `message` VARCHAR(500) NOT NULL,
  `resource_type` ENUM('video', 'comment', 'user', 'system') NULL DEFAULT NULL,
  `resource_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_notif_user` (`user_id`, `is_read`, `created_at` DESC),
  CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_notif_sender` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 19. TABLA: auth_sessions (Sesiones y Tokens de Autenticación)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `auth_sessions`;
CREATE TABLE `auth_sessions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `refresh_token_hash` VARCHAR(255) NOT NULL,
  `user_agent` VARCHAR(255) NULL DEFAULT NULL,
  `ip_address` VARCHAR(45) NULL DEFAULT NULL,
  `is_revoked` BOOLEAN NOT NULL DEFAULT FALSE,
  `expires_at` DATETIME NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_auth_user` (`user_id`),
  KEY `idx_auth_expires` (`expires_at`),
  CONSTRAINT `fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 20. TABLA: stories (Historias efímeras de 24 horas - TikTok/Instagram Stories)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `stories`;
CREATE TABLE `stories` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `media_url` VARCHAR(500) NOT NULL,
  `media_type` ENUM('video', 'image') NOT NULL DEFAULT 'video',
  `caption` VARCHAR(300) NULL DEFAULT NULL,
  `duration_seconds` DECIMAL(5, 2) NOT NULL DEFAULT 5.00,
  `audience_rating` ENUM('all_ages', 'teen', 'mature', 'restricted') NOT NULL DEFAULT 'all_ages',
  `moderation_status` ENUM('approved', 'under_review', 'rejected') NOT NULL DEFAULT 'approved',
  `views_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `expires_at` DATETIME NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_stories_user` (`user_id`),
  KEY `idx_stories_expires` (`expires_at`),
  KEY `idx_stories_active` (`expires_at`, `moderation_status`),
  CONSTRAINT `fk_stories_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 21. TABLA: story_views (Registro de visualizaciones únicas de historias)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `story_views`;
CREATE TABLE `story_views` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `story_id` BIGINT UNSIGNED NOT NULL,
  `viewer_user_id` BIGINT UNSIGNED NOT NULL,
  `viewed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_story_viewer` (`story_id`, `viewer_user_id`),
  KEY `idx_story_views_viewer` (`viewer_user_id`),
  CONSTRAINT `fk_story_views_story` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_story_views_user` FOREIGN KEY (`viewer_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reactivar verificación de llaves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- FIN DEL SCRIPT DDL
-- =============================================================================
