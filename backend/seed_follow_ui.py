"""
================================================================================
PROYECTO FOLLOW - SCRIPT DE POBLACIÓN DE DATOS EXACTOS DE LA INTERFAZ UI
================================================================================
Puebla la base de datos MySQL (Laragon) con las cuentas, videos, sonidos,
hashtags, historias y comentarios exactos que aparecen en los diseños de Stitch.
Cumple con las normas de tipado e integridad referencial de MySQL 8.
================================================================================
"""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import (
    Base, engine, SessionLocal, UserModel,
    SoundModel, VideoModel, HashtagModel, VideoHashtagModel,
    VideoLikeModel, CommentModel, FollowModel, SavedVideoModel,
    StoryModel, StoryViewModel
)
from backend.core.security import hash_password

def seed_follow_ui():
    print("Iniciando sembrado de datos UI para Follow...")
    db = SessionLocal()
    try:
        pwd = hash_password("valeria123")
        pwd_user = hash_password("user123")

        # 1. Creadora Principal: Valeria Gómez (@valeria_creatrix)
        valeria = db.query(UserModel).filter(UserModel.username == "valeria_creatrix").first()
        if not valeria:
            valeria = UserModel(
                username="valeria_creatrix",
                email="valeria@follow.io",
                password_hash=pwd,
                full_name="Valeria Gómez",
                bio="Directora de arte & creadora digital | Tech & Urban Lifestyle | Collabs: valeria@follow.io | Madrid / Tokyo",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500",
                birth_date=date(1996, 4, 15),
                role="creator",
                account_type="standard",
                is_verified=True,
                is_active=True
            )
            db.add(valeria)
            db.commit()
            db.refresh(valeria)
            print("Creada usuaria @valeria_creatrix")

        # 2. Creadora en Vivo: Sofia K (@sofia.k)
        sofia_k = db.query(UserModel).filter(UserModel.username == "sofia.k").first()
        if not sofia_k:
            sofia_k = UserModel(
                username="sofia.k",
                email="sofia.k@follow.tv",
                password_hash=pwd_user,
                full_name="Sofia K",
                bio="Explorando nuevas frecuencias visuales en el showcase nocturno de Tokio",
                avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500",
                birth_date=date(1999, 8, 22),
                role="creator",
                account_type="standard",
                is_verified=True,
                is_active=True
            )
            db.add(sofia_k)
            db.commit()
            db.refresh(sofia_k)
            print("Creada usuaria @sofia.k")

        # 3. Cuentas Sugeridas de Explorar
        creators_data = [
            ("kira_techwear", "kira@follow.tv", "Kira Vex", "Cyberpunk fashion designer and techwear enthusiast", "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=500", 842000),
            ("neo_shibuya", "shibuya@follow.tv", "NeoShibuya_Lab", "Tokyo future aesthetics and street style", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=500", 1200000),
            ("aeroghost_fits", "aero@follow.tv", "AeroGhost", "Tactical gear and dark wear curation", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", 490000),
            ("cypher.couture", "cypher@follow.tv", "Cypher Couture", "Haute couture meets cybernetic dystopianism", "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500", 315000),
            ("mateo_vfx", "mateo@follow.tv", "mateo_vfx", "VFX Artist & Colorist", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500", 120000),
            ("clara_design", "clara@follow.tv", "clara_design", "Motion Graphics & Visual Rhythm", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500", 98000),
            ("dev_raul", "raul@follow.tv", "dev_raul", "Creative Technologist", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=500", 45000),
            ("alex_neon", "alex@follow.tv", "Alex Neon", "Hardware modder and lighting designer", "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=500", 78000),
            ("cyberluna", "luna@follow.tv", "CyberLuna", "VR World Builder & 3D Sculptor", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500", 160000),
            ("marcos.creator", "marcos.creator@follow.tv", "Marcos Creator", "Digital Content Creator", "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=500", 25000)
        ]

        creator_objs = {}
        for uname, uemail, ufullname, ubio, uavatar, _ in creators_data:
            u = db.query(UserModel).filter(UserModel.username == uname).first()
            if not u:
                u = UserModel(
                    username=uname,
                    email=uemail,
                    password_hash=pwd_user,
                    full_name=ufullname,
                    bio=ubio,
                    avatar_url=uavatar,
                    birth_date=date(1995, 2, 10),
                    role="creator",
                    account_type="standard",
                    is_verified=True,
                    is_active=True
                )
                db.add(u)
                db.commit()
                db.refresh(u)
            creator_objs[uname] = u

        # 4. Pistas de Sonido
        sounds_data = [
            ("Original Sound - Valeria Studio", "Valeria Studio", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=150", 45, 248600),
            ("Synthetic Pulse (Overdrive Edit)", "Kavinsky x Vector Seven", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=150", 45, 142800),
            ("Neo Tokyo Rain Drift (Night Version)", "Subway Runner Collective", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=150", 32, 88400),
            ("Neon Horizon Beat", "Sofia K & Cyber Night", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=150", 60, 1800000),
            ("Midnight Synthwave • Neon Drift", "Retro Synth Lab", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=150", 45, 95000)
        ]
        sound_objs = {}
        for stitle, sartist, surl, scover, sdur, susage in sounds_data:
            s = db.query(SoundModel).filter(SoundModel.title == stitle).first()
            if not s:
                s = SoundModel(
                    title=stitle,
                    artist_name=sartist,
                    audio_url=surl,
                    cover_url=scover,
                    duration_seconds=sdur,
                    usage_count=susage
                )
                db.add(s)
                db.commit()
                db.refresh(s)
            sound_objs[stitle] = s

        # 5. Hashtags
        hashtags_data = [
            ("CyberpunkStyle", 1540, 43200000),
            ("StreetwearInspo", 3200, 128000000),
            ("NeonVibes", 2100, 89000000),
            ("TechwearFits", 4100, 214600000),
            ("DystopianFashion", 980, 32800000),
            ("aesthetic", 5400, 350000000),
            ("techtrends", 1800, 95000000),
            ("creativelife", 2300, 110000000),
            ("cyberpunk", 6200, 420000000),
            ("follow", 15000, 900000000),
            ("tech", 8200, 520000000),
            ("setup", 4100, 260000000),
            ("creator", 3900, 180000000),
            ("viral", 25000, 1500000000)
        ]
        tag_objs = {}
        for tname, vcount, views in hashtags_data:
            t = db.query(HashtagModel).filter(HashtagModel.tag == tname).first()
            if not t:
                t = HashtagModel(tag=tname, videos_count=vcount, views_count=views)
                db.add(t)
                db.commit()
                db.refresh(t)
            tag_objs[tname] = t

        # 6. Videos para Valeria Gómez
        valeria_videos = [
            {
                "title": "Cyberpunk Street Wear 2025",
                "description": "Exploración de siluetas utilitarias y textiles reflectantes en el distrito de Shibuya. #CyberpunkStyle #StreetwearInspo",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600",
                "views": 2400000,
                "likes": 410000,
                "comments": 1420,
                "tags": ["CyberpunkStyle", "StreetwearInspo"]
            },
            {
                "title": "Mi proceso de diseño inmersivo",
                "description": "Cómo combino modelado espacial en VR con texturas analógicas. #creativelife #aesthetic",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=600",
                "views": 1200000,
                "likes": 180000,
                "comments": 850,
                "tags": ["creativelife", "aesthetic"]
            },
            {
                "title": "Morning ritual en Madrid",
                "description": "Café de especialidad, orden en la mesa y plan de rodaje. #aesthetic #lifestyle",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600",
                "views": 890000,
                "likes": 95000,
                "comments": 420,
                "tags": ["aesthetic"]
            },
            {
                "title": "Akihabara a las 3 AM",
                "description": "Luces de neón solitarias y pasillos retro gaming en Tokyo. #cyberpunk #neonvibes",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=600",
                "views": 540000,
                "likes": 78000,
                "comments": 310,
                "tags": ["NeonVibes", "cyberpunk"]
            },
            {
                "title": "ASMR Custom Keyboard Build",
                "description": "Lubricando switches mecánicos lineales con chasis de aluminio pulido. #tech #setup",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
                "views": 520000,
                "likes": 63000,
                "comments": 290,
                "tags": ["tech", "setup"]
            },
            {
                "title": "3 Hacks de luz con el móvil",
                "description": "Prismas de cristal, dispersión RGB y reflejos en pantalla. #techtrends #creator",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?w=600",
                "views": 450000,
                "likes": 42000,
                "comments": 195,
                "tags": ["techtrends", "creator"]
            },
            {
                "title": "¿Mi nueva cámara principal?",
                "description": "Unboxing y primeras pruebas con sensor de cine full-frame. #creator #tech",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600",
                "views": 398000,
                "likes": 37000,
                "comments": 180,
                "tags": ["creator", "tech"]
            },
            {
                "title": "Sampleando sonidos del metro",
                "description": "Capturando frecuencias subterráneas para un nuevo track synthwave. #aesthetic #cyberpunk",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
                "thumbnail_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600",
                "views": 312000,
                "likes": 29000,
                "comments": 140,
                "tags": ["aesthetic", "cyberpunk"]
            }
        ]

        # Video del Feed (Pantalla 4)
        feed_video = db.query(VideoModel).filter(VideoModel.title == "Configurando el nuevo setup holográfico para streaming nocturno").first()
        if not feed_video:
            feed_video = VideoModel(
                user_id=valeria.id,
                sound_id=sound_objs["Original Sound - Valeria Studio"].id,
                title="Configurando el nuevo setup holográfico para streaming nocturno",
                description="Configurando el nuevo setup holográfico para streaming nocturno. ¿Qué opinan de esta distribución? #aesthetic #techtrends #creativelife #cyberpunk",
                video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                thumbnail_url="https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600",
                duration_seconds=34.0,
                views_count=3481200,
                likes_count=1200000,
                comments_count=34812,
                shares_count=15400,
                visibility="public",
                allow_comments=True,
                allow_duet=True,
                audience_rating="all_ages",
                moderation_status="approved"
            )
            db.add(feed_video)
            db.commit()
            db.refresh(feed_video)

            # Comentarios del feed
            comments_feed = [
                (creator_objs["mateo_vfx"], "¡La corrección de color está a otro nivel! ¿Estás usando LUTs personalizados de DaVinci?", 1420),
                (valeria, "¡Dejé el link con todos los presets y el breakdown en la bio de mi perfil! Gracias por el apoyo familia", 3890),
                (creator_objs["clara_design"], "El ritmo de la música con las transiciones es pura magia visual. Necesito tutorial urgente", 248),
                (creator_objs["dev_raul"], "Increíble render. ¿Cuánto tardó en exportar ese tracking de cámara?", 89)
            ]
            for u_comm, c_text, c_likes in comments_feed:
                c = CommentModel(
                    video_id=feed_video.id,
                    user_id=u_comm.id,
                    content=c_text,
                    likes_count=c_likes,
                    moderation_status="approved"
                )
                db.add(c)
            db.commit()

        # Insertar videos de perfil
        for v in valeria_videos:
            existing = db.query(VideoModel).filter(VideoModel.title == v["title"]).first()
            if not existing:
                nv = VideoModel(
                    user_id=valeria.id,
                    sound_id=sound_objs["Original Sound - Valeria Studio"].id,
                    title=v["title"],
                    description=v["description"],
                    video_url=v["video_url"],
                    thumbnail_url=v["thumbnail_url"],
                    duration_seconds=20.0,
                    views_count=v["views"],
                    likes_count=v["likes"],
                    comments_count=v["comments"],
                    shares_count=int(v["likes"] * 0.05),
                    visibility="public",
                    allow_comments=True,
                    allow_duet=True,
                    audience_rating="all_ages",
                    moderation_status="approved"
                )
                db.add(nv)
                db.commit()
                db.refresh(nv)
                for tname in v["tags"]:
                    if tname in tag_objs:
                        vh = VideoHashtagModel(video_id=nv.id, hashtag_id=tag_objs[tname].id)
                        db.add(vh)
                db.commit()

        # 7. Videos de Explorar (Pantalla 3)
        explore_videos = [
            ("Top 5 marcas underground de Cyberpunk Streetwear para...", creator_objs["kira_techwear"], 1800000, 145000, "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600"),
            ("Cómo estilizar un chaleco táctico con piezas oversize...", creator_objs["aeroghost_fits"], 890000, 68000, "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600"),
            ("Outfit check en Akihabara a medianoche: cyberpunk pur...", creator_objs["neo_shibuya"], 2300000, 230000, "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600"),
            ("DIY: Cómo poner luces fibra óptica en tu sudadera negra...", creator_objs["alex_neon"], 540000, 42000, "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=600"),
            ("Neo-Samurai: Fusión entre folclore y techwear distópic...", creator_objs["cypher.couture"], 3100000, 398000, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600"),
            ("Unboxing de los sneakers más ciberpunk del mercado:...", creator_objs["dev_raul"], 970000, 81000, "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600")
        ]

        for etitle, eauthor, eviews, elikes, ethumb in explore_videos:
            existing = db.query(VideoModel).filter(VideoModel.title == etitle).first()
            if not existing:
                ev = VideoModel(
                    user_id=eauthor.id,
                    sound_id=sound_objs["Synthetic Pulse (Overdrive Edit)"].id,
                    title=etitle,
                    description=f"{etitle} #CyberpunkStyle #StreetwearInspo #TechwearFits",
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                    thumbnail_url=ethumb,
                    duration_seconds=25.0,
                    views_count=eviews,
                    likes_count=elikes,
                    comments_count=int(elikes * 0.08),
                    shares_count=int(elikes * 0.04),
                    visibility="public",
                    allow_comments=True,
                    allow_duet=True,
                    audience_rating="all_ages",
                    moderation_status="approved"
                )
                db.add(ev)
                db.commit()
                db.refresh(ev)
                for tname in ["CyberpunkStyle", "StreetwearInspo", "TechwearFits"]:
                    if tname in tag_objs:
                        db.add(VideoHashtagModel(video_id=ev.id, hashtag_id=tag_objs[tname].id))
                db.commit()

        # 8. Historias Destacadas de Valeria Gómez
        now = datetime.now(timezone.utc)
        highlights = [
            ("Tokyo '24", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=600"),
            ("Setup 4.0", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600"),
            ("Outfits", "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600"),
            ("Festivales", "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600")
        ]
        for htitle, hmedia in highlights:
            existing = db.query(StoryModel).filter(StoryModel.caption == htitle, StoryModel.user_id == valeria.id).first()
            if not existing:
                st = StoryModel(
                    user_id=valeria.id,
                    media_url=hmedia,
                    media_type="image",
                    caption=htitle,
                    duration_seconds=5.0,
                    audience_rating="all_ages",
                    moderation_status="approved",
                    views_count=1840,
                    expires_at=now + timedelta(days=365),
                    created_at=now
                )
                db.add(st)
        db.commit()

        # 9. Relaciones de Seguimiento para Valeria (348 seguidos, creadores seguidores)
        for cname in ["kira_techwear", "neo_shibuya", "aeroghost_fits"]:
            c_target = creator_objs[cname]
            f = db.query(FollowModel).filter(FollowModel.follower_id == valeria.id, FollowModel.following_id == c_target.id).first()
            if not f:
                db.add(FollowModel(follower_id=valeria.id, following_id=c_target.id, status="active"))
            f2 = db.query(FollowModel).filter(FollowModel.follower_id == c_target.id, FollowModel.following_id == valeria.id).first()
            if not f2:
                db.add(FollowModel(follower_id=c_target.id, following_id=valeria.id, status="active"))
        db.commit()

        print("Población de datos Follow UI completada exitosamente en MySQL Laragon.")

    except Exception as e:
        db.rollback()
        print(f"Error al poblar datos Follow: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_follow_ui()
