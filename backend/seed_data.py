"""
================================================================================
PROYECTO SOFÍA - SCRIPT GENERADOR DE DATOS SEMILLA (SEED DATA)
================================================================================
Genera usuarios de prueba (admin, creadores, menor y tutor), sonidos,
hashtags, videos con métricas, comentarios, likes y vinculación parental.
Ideal para alimentar la base de datos y probar la API y el Frontend al 100%.
================================================================================
"""

import sys
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

# Añadir raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import (
    Base, engine, SessionLocal, UserModel, ParentalControlModel,
    SoundModel, VideoModel, HashtagModel, VideoHashtagModel,
    VideoLikeModel, CommentModel, FollowModel, SavedVideoModel,
    ParentChildLinkModel, NotificationModel, StoryModel, StoryViewModel
)
from backend.core.security import hash_password
from backend.reglas.parental_control import ParentalControlManager


def seed_database():
    print("Iniciando creación de datos semilla para Proyecto Sofía...")

    # Crear tablas si no existen aún (por ejemplo si se usa en SQLite o MySQL)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. USUARIOS DE PRUEBA
        existing_admin = db.query(UserModel).filter(UserModel.username == "admin").first()
        if existing_admin:
            # Verificar si faltan historias por sembrar
            if not db.query(StoryModel).first():
                user_sofia = db.query(UserModel).filter(UserModel.username == "sofia_oficial").first()
                user_carlos = db.query(UserModel).filter(UserModel.username == "carlos_dancer").first()
                user_ana = db.query(UserModel).filter(UserModel.username == "ana_menor").first()
                if user_sofia and user_carlos:
                    print("-> Sembrando historias para usuarios existentes...")
                    _seed_stories(db, user_sofia, user_carlos, user_ana)
                    print(" Historias agregadas a la base de datos.")
            print(" Los datos semilla ya se encuentran cargados en la base de datos.")
            return

        print("-> Creando usuarios principales...")
        pwd_admin = hash_password("admin123")
        pwd_user = hash_password("sofia123")

        users = [
            UserModel(
                username="admin",
                email="admin@sofia.app",
                password_hash=pwd_admin,
                full_name="Administrador Sofía",
                bio="Cuenta oficial de administración del sistema.",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                birth_date=date(1990, 5, 20),
                role="admin",
                account_type="standard",
                is_verified=True,
                is_active=True
            ),
            UserModel(
                username="moderador",
                email="moderador@sofia.app",
                password_hash=pwd_user,
                full_name="Equipo de Moderación",
                bio="Garantizando un entorno seguro para todos los usuarios.",
                avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                birth_date=date(1995, 8, 12),
                role="moderator",
                account_type="standard",
                is_verified=True,
                is_active=True
            ),
            UserModel(
                username="sofia_oficial",
                email="sofia@sofia.app",
                password_hash=pwd_user,
                full_name="Sofía Creadora Oficial",
                bio="Bailarina, creadora de contenido y entusiasta de la música  #DanceLife",
                avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
                birth_date=date(2001, 3, 15),
                role="creator",
                account_type="standard",
                is_verified=True,
                is_active=True
            ),
            UserModel(
                username="carlos_dancer",
                email="carlos@sofia.app",
                password_hash=pwd_user,
                full_name="Carlos Rivas",
                bio="Coreógrafo urbano. Retos diarios de baile y tutoriales 💃🕺",
                avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
                birth_date=date(1998, 11, 4),
                role="creator",
                account_type="standard",
                is_verified=False,
                is_active=True
            ),
            UserModel(
                username="pedro_padre",
                email="pedro@familia.com",
                password_hash=pwd_user,
                full_name="Pedro Martínez (Padre)",
                bio="Tutor de familia y supervisor.",
                avatar_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
                birth_date=date(1982, 1, 10),
                role="user",
                account_type="parent",
                is_verified=False,
                is_active=True
            ),
            UserModel(
                username="ana_menor",
                email="ana@familia.com",
                password_hash=pwd_user,
                full_name="Ana Martínez",
                bio="Amo dibujar, cocinar galletas y bailar 🎨🍪",
                avatar_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150",
                birth_date=date(2011, 6, 25),  # Menor de 15 años
                role="user",
                account_type="minor",
                is_verified=False,
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()

        # Recargar IDs
        user_admin = db.query(UserModel).filter(UserModel.username == "admin").first()
        user_mod = db.query(UserModel).filter(UserModel.username == "moderador").first()
        user_sofia = db.query(UserModel).filter(UserModel.username == "sofia_oficial").first()
        user_carlos = db.query(UserModel).filter(UserModel.username == "carlos_dancer").first()
        user_pedro = db.query(UserModel).filter(UserModel.username == "pedro_padre").first()
        user_ana = db.query(UserModel).filter(UserModel.username == "ana_menor").first()

        # 2. CONTROL PARENTAL Y VINCULACIÓN FAMILIAR PARA LA MENOR
        print("-> Configurando control parental y vinculación familiar...")
        pin_hash = ParentalControlManager.hash_parental_pin("2026")
        parental_ana = ParentalControlModel(
            user_id=user_ana.id,
            is_enabled=True,
            pin_hash=pin_hash,
            daily_screen_time_limit_minutes=90,
            curfew_start_time=time(22, 0),
            curfew_end_time=time(6, 0),
            restricted_mode=True,
            block_direct_messages=True,
            filter_mature_comments=True,
            allow_search=True
        )
        db.add(parental_ana)

        # Vincular cuenta padre-hijo
        link = ParentChildLinkModel(
            parent_user_id=user_pedro.id,
            child_user_id=user_ana.id,
            status="active",
            linked_at=datetime.now(timezone.utc)
        )
        db.add(link)
        db.commit()

        # 3. PISTAS DE AUDIO / SONIDOS
        print("-> Creando catálogo de pistas de sonido...")
        sounds = [
            SoundModel(
                title="Trend Beat 2026 (Original)",
                artist_name="DJ Sofía",
                audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                cover_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=150",
                duration_seconds=45,
                usage_count=1240
            ),
            SoundModel(
                title="Acoustic Summer Vibes",
                artist_name="Acoustic Project",
                audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                cover_url="https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=150",
                duration_seconds=30,
                usage_count=850
            ),
            SoundModel(
                title="Urban Hip Hop Loop",
                artist_name="Carlos Rivas Beat",
                audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
                cover_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=150",
                duration_seconds=60,
                usage_count=620
            )
        ]
        db.add_all(sounds)
        db.commit()

        sound_trend = db.query(SoundModel).filter(SoundModel.title == "Trend Beat 2026 (Original)").first()
        sound_acoustic = db.query(SoundModel).filter(SoundModel.title == "Acoustic Summer Vibes").first()

        # 4. HASHTAGS
        print("-> Creando tendencias de hashtags...")
        hashtags_data = [
            ("baile", 15, 3200),
            ("tendencias", 25, 5400),
            ("humor", 10, 2100),
            ("cocina", 8, 1450),
            ("musica", 18, 4100),
            ("educacion", 5, 890),
            ("sofia", 20, 6200)
        ]
        for tag_name, vcount, views in hashtags_data:
            tag_obj = HashtagModel(tag=tag_name, videos_count=vcount, views_count=views)
            db.add(tag_obj)
        db.commit()

        tag_baile = db.query(HashtagModel).filter(HashtagModel.tag == "baile").first()
        tag_tend = db.query(HashtagModel).filter(HashtagModel.tag == "tendencias").first()
        tag_humor = db.query(HashtagModel).filter(HashtagModel.tag == "humor").first()
        tag_cocina = db.query(HashtagModel).filter(HashtagModel.tag == "cocina").first()

        # 5. VIDEOS CORTOS (Vertical Videos con enlaces reales para demo)
        print("-> Publicando videos de demostración...")
        # Videos cortos públicos reproducibles en HTML5
        sample_videos = [
            {
                "author": user_sofia,
                "sound": sound_trend,
                "title": "Nuevo reto de baile viral 💃✨ ¿Quién se anima a hacerlo?",
                "description": "Practicando esta coreografía desde temprano. ¡Etiquétame si haces el dúo! #baile #tendencias #sofia",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1547153760-18fc86324498?w=500",
                "duration": 15.0,
                "views": 4200,
                "likes": 830,
                "comments": 45,
                "shares": 120,
                "rating": "all_ages",
                "tags": [tag_baile, tag_tend]
            },
            {
                "author": user_carlos,
                "sound": sound_trend,
                "title": "Tutorial paso a paso: Giro con estilo urbano 👟🔥",
                "description": "Aprende este paso en menos de 1 minuto. Fácil y con mucha actitud. #baile #tendencias",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500",
                "duration": 22.0,
                "views": 3100,
                "likes": 540,
                "comments": 28,
                "shares": 95,
                "rating": "all_ages",
                "tags": [tag_baile]
            },
            {
                "author": user_ana,
                "sound": sound_acoustic,
                "title": "Decorando galletas caseras de chispas de chocolate 🍪👩‍🍳",
                "description": "Receta súper fácil para hacer en familia una tarde de domingo. #cocina #tendencias",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500",
                "duration": 18.0,
                "views": 1850,
                "likes": 410,
                "comments": 19,
                "shares": 30,
                "rating": "all_ages",
                "tags": [tag_cocina, tag_tend]
            },
            {
                "author": user_sofia,
                "sound": sound_acoustic,
                "title": "Cuando intentas cocinar algo elegante y sale así 😅",
                "description": "Expectativa vs Realidad versión chef. No intenten esto en casa jaja. #humor #cocina",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=500",
                "duration": 14.0,
                "views": 5900,
                "likes": 1250,
                "comments": 78,
                "shares": 210,
                "rating": "all_ages",
                "tags": [tag_humor, tag_cocina]
            },
            {
                "author": user_carlos,
                "sound": sound_trend,
                "title": "Batalla de pasos con el crew en el parque ⚡🏆",
                "description": "Mucha energía en la sesión de hoy. ¿Cuál de los 3 pasos fue tu favorito? #baile #tendencias",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=500",
                "duration": 25.0,
                "views": 2800,
                "likes": 490,
                "comments": 33,
                "shares": 60,
                "rating": "teen",
                "tags": [tag_baile]
            }
        ]

        created_videos = []
        for vdata in sample_videos:
            v_obj = VideoModel(
                user_id=vdata["author"].id,
                sound_id=vdata["sound"].id if vdata["sound"] else None,
                title=vdata["title"],
                description=vdata["description"],
                video_url=vdata["video_url"],
                thumbnail_url=vdata["thumbnail_url"],
                duration_seconds=vdata["duration"],
                views_count=vdata["views"],
                likes_count=vdata["likes"],
                comments_count=vdata["comments"],
                shares_count=vdata["shares"],
                visibility="public",
                allow_comments=True,
                allow_duet=True,
                audience_rating=vdata["rating"],
                moderation_status="approved"
            )
            db.add(v_obj)
            db.commit()
            db.refresh(v_obj)

            # Asociar etiquetas
            for t in vdata["tags"]:
                vh = VideoHashtagModel(video_id=v_obj.id, hashtag_id=t.id)
                db.add(vh)

            created_videos.append(v_obj)

        db.commit()

        # 6. COMENTARIOS Y LIKES INTERACTIVOS
        print("-> Agregando comentarios y likes iniciales...")
        first_video = created_videos[0]
        comments_data = [
            (user_carlos, "¿En qué ciudad estás grabando? Quedó brutal el ritmo! 🔥"),
            (user_ana, "¡Me encantó el paso final, lo voy a intentar! ✨"),
            (user_pedro, "Excelente contenido y muy sano para los jóvenes. Saludos."),
            (user_mod, "Contenido verificado y aprobado según las normas de la comunidad.")
        ]
        for author_comment, text in comments_data:
            comm = CommentModel(
                video_id=first_video.id,
                user_id=author_comment.id,
                content=text,
                likes_count=4,
                moderation_status="approved"
            )
            db.add(comm)

        # Likes de usuarios
        db.add(VideoLikeModel(user_id=user_carlos.id, video_id=first_video.id))
        db.add(VideoLikeModel(user_id=user_ana.id, video_id=first_video.id))
        db.add(VideoLikeModel(user_id=user_pedro.id, video_id=first_video.id))

        # Favoritos
        db.add(SavedVideoModel(user_id=user_ana.id, video_id=first_video.id, collection_name="Favoritos"))

        # Seguidores
        db.add(FollowModel(follower_id=user_carlos.id, following_id=user_sofia.id, status="active"))
        db.add(FollowModel(follower_id=user_ana.id, following_id=user_sofia.id, status="active"))
        db.add(FollowModel(follower_id=user_pedro.id, following_id=user_carlos.id, status="active"))

        # Notificaciones
        db.add(NotificationModel(
            user_id=user_sofia.id,
            sender_id=user_carlos.id,
            type="new_like",
            title="¡Nuevo Me Gusta!",
            message=f"A @{user_carlos.username} le gustó tu video '{first_video.title[:30]}...'",
            resource_type="video",
            resource_id=first_video.id,
            is_read=False
        ))
        db.add(NotificationModel(
            user_id=user_sofia.id,
            sender_id=user_ana.id,
            type="new_follower",
            title="¡Nuevo Seguidor!",
            message=f"@{user_ana.username} ha comenzado a seguirte.",
            resource_type="user",
            resource_id=user_ana.id,
            is_read=False
        ))

        # Historias (Stories 24h)
        _seed_stories(db, user_sofia, user_carlos, user_ana)

        db.commit()
        print("================================================================")
        print(" ¡DATOS SEMILLA CARGADOS EXITOSAMENTE EN PROYECTO SOFÍA!")
        print("================================================================")
        print(" Usuarios creados (contraseña: admin123 para admin / sofia123 para el resto):")
        print("  - @admin           (Rol: Administrador)")
        print("  - @moderador       (Rol: Moderador)")
        print("  - @sofia_oficial   (Rol: Creador verificado)")
        print("  - @carlos_dancer   (Rol: Creador)")
        print("  - @ana_menor       (Rol: Menor con Control Parental y PIN '2026')")
        print("  - @pedro_padre     (Rol: Padre/Tutor vinculado a @ana_menor)")
        print(" Pistas de sonido: 3 canciones")
        print(" Hashtags: #baile, #tendencias, #humor, #cocina, #musica, #sofia")
        print(" Videos con feeds listos: 5 videos con métricas, likes y comentarios")
        print(" Historias de 24h: 3 historias activas con visualizaciones")
        print("================================================================")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al sembrar datos: {e}")
        raise e
    finally:
        db.close()


def _seed_stories(db, user_sofia, user_carlos, user_ana):
    now = datetime.now(timezone.utc)
    story1 = StoryModel(
        user_id=user_sofia.id,
        media_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        media_type="video",
        caption="¡Preparando nueva coreografía para hoy! ✨💃",
        duration_seconds=10.0,
        audience_rating="all_ages",
        moderation_status="approved",
        views_count=1,
        expires_at=now + timedelta(hours=24),
        created_at=now
    )
    story2 = StoryModel(
        user_id=user_sofia.id,
        media_url="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
        media_type="image",
        caption="Luces encendidas en el estudio 🎶🔥",
        duration_seconds=5.0,
        audience_rating="all_ages",
        moderation_status="approved",
        views_count=0,
        expires_at=now + timedelta(hours=23),
        created_at=now
    )
    story3 = StoryModel(
        user_id=user_carlos.id,
        media_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        media_type="video",
        caption="Reto de baile callejero aceptado 💥",
        duration_seconds=8.0,
        audience_rating="all_ages",
        moderation_status="approved",
        views_count=0,
        expires_at=now + timedelta(hours=22),
        created_at=now
    )
    db.add_all([story1, story2, story3])
    db.commit()
    db.refresh(story1)

    if user_ana:
        db.add(StoryViewModel(story_id=story1.id, viewer_user_id=user_ana.id, viewed_at=now))
        db.commit()
    print("-> Historias sembradas con éxito.")


if __name__ == "__main__":
    seed_database()
