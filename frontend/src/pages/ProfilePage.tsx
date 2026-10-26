/**
 * Pantalla 1: Perfil de Usuario y Contenido (Valeria Gomez).
 * Totalmente programada con gestion de pestañas (Reels, Guardados, Borradores, Me Gusta),
 * modales interactivos para Editar Perfil, Compartir Perfil, Estadisticas de Creador y Ajustes de Cuenta.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircle, Headphones, MapPin, Music2, Video as VideoIcon, 
  Pencil, Share2, TrendingUp, Settings, Plus, Film, Bookmark, 
  Archive, Heart, Lock, Grid, List, Play, Pause, ChevronRight, X, 
  ChevronLeft, Send, Sparkles, Upload, Copy, Check, Shield, 
  Eye, Folder, ArrowRight, Volume2, VolumeX, MessageSquare
} from 'lucide-react';
import { SettingsModal } from '../components/settings/SettingsModal';

interface HighlightStory {
  id: string;
  title: string;
  image: string;
  date?: string;
}

interface ProfileVideo {
  id: number;
  title: string;
  views: string;
  likes: string;
  image: string;
  videoUrl: string;
  description?: string;
  soundTitle?: string;
  tags?: string[];
  isPinned?: boolean;
  hasAudioNote?: boolean;
}

interface SavedCollection {
  id: string;
  title: string;
  count: number;
  cover: string;
}

interface DraftItem {
  id: string;
  title: string;
  modified: string;
  duration: string;
  image: string;
}

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'reels' | 'saved' | 'drafts' | 'liked'>('reels');
  const [isFollowing, setIsFollowing] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<ProfileVideo | null>(null);

  // Estados de Modales de Accion del Perfil
  const [showEditProfileModal, setShowEditProfileModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  // Estados del Reproductor de Video en Modal
  const [isVideoPlaying, setIsVideoPlaying] = useState(true);
  const [isVideoMuted, setIsVideoMuted] = useState(true);
  const [modalVideoProgress, setModalVideoProgress] = useState(0);
  const [modalLikedMap, setModalLikedMap] = useState<Record<number, boolean>>({});
  const [modalBookmarksMap, setModalBookmarksMap] = useState<Record<number, boolean>>({});
  const modalVideoRef = useRef<HTMLVideoElement>(null);
  const modalTouchStartX = useRef<number | null>(null);
  const modalTouchStartY = useRef<number | null>(null);

  // Soporte de navegacion por gestos tactiles (Swipe horizontal y vertical) en el modal de video
  const handleModalTouchStart = (e: React.TouchEvent) => {
    modalTouchStartX.current = e.touches[0].clientX;
    modalTouchStartY.current = e.touches[0].clientY;
  };

  const handleModalTouchEnd = (e: React.TouchEvent) => {
    if (modalTouchStartX.current === null || modalTouchStartY.current === null || !selectedVideo) return;
    const deltaX = modalTouchStartX.current - e.changedTouches[0].clientX;
    const deltaY = modalTouchStartY.current - e.changedTouches[0].clientY;

    if (Math.abs(deltaY) > Math.abs(deltaX)) {
      if (deltaY > 45) {
        // Deslizar arriba -> siguiente video
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const nextIndex = (currentIndex + 1) % reelsVideos.length;
        setSelectedVideo(reelsVideos[nextIndex]);
      } else if (deltaY < -45) {
        // Deslizar abajo -> video anterior
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const prevIndex = (currentIndex - 1 + reelsVideos.length) % reelsVideos.length;
        setSelectedVideo(reelsVideos[prevIndex]);
      }
    } else {
      if (deltaX > 45) {
        // Deslizar izquierda -> siguiente video
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const nextIndex = (currentIndex + 1) % reelsVideos.length;
        setSelectedVideo(reelsVideos[nextIndex]);
      } else if (deltaX < -45) {
        // Deslizar derecha -> video anterior
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const prevIndex = (currentIndex - 1 + reelsVideos.length) % reelsVideos.length;
        setSelectedVideo(reelsVideos[prevIndex]);
      }
    }

    modalTouchStartX.current = null;
    modalTouchStartY.current = null;
  };

  // Datos Editables del Perfil
  const [profileData, setProfileData] = useState({
    fullName: "Valeria Gomez",
    username: "valeria_creatrix",
    bio: "Directora de arte & creadora digital | Tech & Urban Lifestyle | Collabs: valeria@follow.io | Madrid / Tokyo",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
    emailCollab: "valeria@follow.io",
    city: "Madrid / Tokyo"
  });

  // Estados del Visor de Historias
  const [activeStoryIndex, setActiveStoryIndex] = useState<number | null>(null);
  const [storyProgress, setStoryProgress] = useState(0);
  const [isStoryPaused, setIsStoryPaused] = useState(false);

  // Modal para Crear Nueva Historia (+ Nuevo)
  const [showNewStoryModal, setShowNewStoryModal] = useState(false);
  const [newStoryTitle, setNewStoryTitle] = useState('');
  const [newStoryImage, setNewStoryImage] = useState('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600');

  // Historias destacadas
  const [highlights, setHighlights] = useState<HighlightStory[]>([
    { id: '1', title: "Tokyo '24", image: "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=600", date: "Julio 2024" },
    { id: '2', title: "Setup 4.0", image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600", date: "Agosto 2024" },
    { id: '3', title: "Outfits", image: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600", date: "Septiembre 2024" },
    { id: '4', title: "Festivales", image: "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600", date: "Octubre 2024" },
  ]);

  // Cuadricula de Reels Publicados (Totalmente vinculados a videos locales HD)
  const reelsVideos: ProfileVideo[] = [
    {
      id: 1,
      title: "Cyberpunk Street Wear 2025",
      views: "2.4M",
      likes: "410K",
      image: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600",
      videoUrl: "/videos/cyber_street.mp4",
      description: "Exploracion de siluetas utilitarias y textiles reflectantes en el distrito de Shibuya.",
      soundTitle: "Synthetic Pulse (Overdrive Edit) - Kavinsky",
      tags: ["#CyberpunkStyle", "#StreetwearInspo", "#Tokyo"],
      isPinned: true
    },
    {
      id: 2,
      title: "Mi proceso de diseno inmersivo",
      views: "1.2M",
      likes: "180K",
      image: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=600",
      videoUrl: "/videos/fashion_walk.mp4",
      description: "Modelado espacial y computacion visual para nuevas pasarelas digitales.",
      soundTitle: "Neo Tokyo Rain Drift - Subway Runner",
      tags: ["#CreativeProcess", "#DigitalArt", "#VR"],
      hasAudioNote: true
    },
    {
      id: 3,
      title: "Morning ritual en Madrid",
      views: "890K",
      likes: "95K",
      image: "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600",
      videoUrl: "/videos/macro_visual.mp4",
      description: "Despertar sereno en Malasana: cafe de especialidad, luz natural y primera sesion de diseno.",
      soundTitle: "Original Sound - Valeria Studio",
      tags: ["#MorningRoutine", "#Madrid", "#CoffeeArt", "#Lifestyle"]
    },
    {
      id: 4,
      title: "Akihabara a las 3 AM",
      views: "540K",
      likes: "78K",
      image: "https://images.unsplash.com/photo-1552053831-71594a27632d?w=600",
      videoUrl: "/videos/city_traffic.mp4",
      description: "Luces de neon, callejones silenciosos y la estetica futurista de Tokyo.",
      soundTitle: "Neon Horizon Beat - Sofia K",
      tags: ["#TokyoNight", "#Akihabara", "#CyberVibes"]
    },
    {
      id: 5,
      title: "ASMR Custom Keyboard Build",
      views: "520K",
      likes: "63K",
      image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
      videoUrl: "/videos/ocean_cinematic.mp4",
      description: "Lubricando switches mecanicos y montando keycaps de ceramica industrial.",
      soundTitle: "ASMR Mechanical Soundscape",
      tags: ["#CustomKeyboard", "#ASMR", "#TechSetup"]
    },
    {
      id: 6,
      title: "3 Hacks de luz con el movil",
      views: "450K",
      likes: "42K",
      image: "https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?w=600",
      videoUrl: "/videos/ambient_people.mp4",
      description: "Iluminacion cinematografica usando pantallas OLED y rebote de luz difusa.",
      soundTitle: "Midnight Synthwave - Neon Drift",
      tags: ["#Filmmaking", "#MobilePhotography", "#Lighting"]
    },
    {
      id: 7,
      title: "Mi nueva camara principal?",
      views: "398K",
      likes: "37K",
      image: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600",
      videoUrl: "/videos/cyber_street.mp4",
      description: "Primeros rollos y pruebas en sensor mediano formato con luz ultravioleta.",
      soundTitle: "Original Sound - Valeria Studio",
      tags: ["#CameraReview", "#MediumFormat", "#Gear"]
    },
    {
      id: 8,
      title: "Sampleando sonidos del metro",
      views: "312K",
      likes: "29K",
      image: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600",
      videoUrl: "/videos/city_traffic.mp4",
      description: "Capturando el ritmo mecanico de los trenes para produccion musical urbana.",
      soundTitle: "Metro Resonance - Sound Design",
      tags: ["#SoundDesign", "#FieldRecording", "#SamplePack"]
    }
  ];

  // Colecciones Guardadas (Tab Guardados 3 colecciones)
  const savedCollections: SavedCollection[] = [
    {
      id: 'c1',
      title: "Inspiracion Cyberpunk & Techwear",
      count: 14,
      cover: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600"
    },
    {
      id: 'c2',
      title: "Tutoriales de Edicion y LUTs",
      count: 8,
      cover: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600"
    },
    {
      id: 'c3',
      title: "Setups de Estudio 2026",
      count: 6,
      cover: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600"
    }
  ];

  // Borradores Activos (Tab Borradores 4 activos)
  const draftVideos: DraftItem[] = [
    {
      id: 'd1',
      title: "Mi nuevo setup nocturno 2025",
      modified: "Hoy, 02:41 AM",
      duration: "00:32",
      image: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600"
    },
    {
      id: 'd2',
      title: "Pruebas de lente anamorfico 35mm en Shibuya",
      modified: "Ayer, 18:20",
      duration: "00:45",
      image: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600"
    },
    {
      id: 'd3',
      title: "Boceto de animacion 3D con shaders causticos",
      modified: "Hace 3 dias",
      duration: "00:15",
      image: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=600"
    },
    {
      id: 'd4',
      title: "Unboxing de microfono shotgun profesional",
      modified: "Hace 5 dias",
      duration: "00:28",
      image: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600"
    }
  ];

  // Temporizador para el visor de historias
  useEffect(() => {
    if (activeStoryIndex === null || isStoryPaused) return;

    const interval = setInterval(() => {
      setStoryProgress((prev) => {
        if (prev >= 100) {
          if (activeStoryIndex < highlights.length - 1) {
            setActiveStoryIndex(activeStoryIndex + 1);
            return 0;
          } else {
            setActiveStoryIndex(null);
            return 0;
          }
        }
        return prev + 2;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [activeStoryIndex, isStoryPaused, highlights.length]);

  // Autoplay y reseteo suave al seleccionar un video en el modal
  useEffect(() => {
    if (selectedVideo) {
      setIsVideoPlaying(true);
      setModalVideoProgress(0);
      if (modalVideoRef.current) {
        modalVideoRef.current.currentTime = 0;
        modalVideoRef.current.play().catch(() => {
          setIsVideoMuted(true);
          if (modalVideoRef.current) {
            modalVideoRef.current.muted = true;
            modalVideoRef.current.play().catch(() => {});
          }
        });
      }
    }
  }, [selectedVideo]);

  // Atajos de teclado dentro del visor de video (Escape para cerrar, Espacio/K pausar, M mutear, Flechas anterior/siguiente)
  useEffect(() => {
    if (!selectedVideo) return;
    const handleModalKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === 'Escape') {
        setSelectedVideo(null);
      } else if (e.key === ' ' || e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (modalVideoRef.current) {
          if (modalVideoRef.current.paused) {
            modalVideoRef.current.play();
            setIsVideoPlaying(true);
          } else {
            modalVideoRef.current.pause();
            setIsVideoPlaying(false);
          }
        }
      } else if (e.key.toLowerCase() === 'm') {
        e.preventDefault();
        setIsVideoMuted(prev => !prev);
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const nextIndex = (currentIndex + 1) % reelsVideos.length;
        setSelectedVideo(reelsVideos[nextIndex]);
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
        const prevIndex = (currentIndex - 1 + reelsVideos.length) % reelsVideos.length;
        setSelectedVideo(reelsVideos[prevIndex]);
      }
    };
    window.addEventListener('keydown', handleModalKeyDown);
    return () => window.removeEventListener('keydown', handleModalKeyDown);
  }, [selectedVideo, reelsVideos]);

  const handleOpenStory = (index: number) => {
    setActiveStoryIndex(index);
    setStoryProgress(0);
    setIsStoryPaused(false);
  };

  const handleCopyProfileLink = () => {
    navigator.clipboard.writeText("https://follow.tv/@valeria_creatrix");
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setShowEditProfileModal(false);
  };

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-12 max-w-7xl mx-auto">
      
      {/* SECCION CABECERA DEL PERFIL */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 sm:gap-8 pt-4 pb-6">
        
        {/* AVATAR E INFORMACION DE VALERIA */}
        <div className="flex items-center gap-4 sm:gap-6">
          <div className="relative flex-shrink-0">
            <div className="w-20 h-20 sm:w-28 sm:h-28 rounded-full p-1 bg-gradient-to-tr from-purple-600 via-pink-500 to-cyan-400 shadow-lg shadow-pink-500/20">
              <img
                src={profileData.avatar}
                alt={profileData.fullName}
                className="w-full h-full rounded-full object-cover border-2 border-[#0c0d14]"
              />
            </div>
          </div>

          <div className="space-y-1 sm:space-y-1.5">
            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <h1 className="text-lg sm:text-2xl font-bold tracking-tight text-white">{profileData.fullName}</h1>
              <CheckCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-cyan-400 fill-cyan-400/20" />
              <span className="text-[9px] sm:text-[10px] font-extrabold uppercase px-1.5 sm:px-2 py-0.5 bg-purple-900/60 text-purple-300 border border-purple-500/30 rounded-md tracking-wider">
                PRO CREATOR
              </span>
            </div>
            <p className="text-xs text-gray-400 font-medium">@{profileData.username}</p>

            <div className="text-xs text-gray-300 space-y-1 pt-1">
              <p className="flex items-center gap-1.5 flex-wrap text-[11px] sm:text-xs">
                <span className="text-pink-400 font-bold">#</span>
                <span>Directora de arte & creadora digital</span>
                <span className="text-gray-600 hidden sm:inline">|</span>
                <span className="hidden sm:inline-flex items-center gap-1">
                  <Headphones className="w-3.5 h-3.5 text-gray-400 inline" />
                  <span>Tech & Urban Lifestyle</span>
                  <span className="text-gray-600">|</span>
                </span>
                <span>Collabs: <a href={`mailto:${profileData.emailCollab}`} className="text-cyan-400 hover:underline">{profileData.emailCollab}</a></span>
                <span className="text-gray-600">|</span>
                <MapPin className="w-3.5 h-3.5 text-rose-400 inline" />
                <span>{profileData.city}</span>
              </p>
            </div>

            <div className="flex items-center gap-2 sm:gap-3 pt-1 text-[10px] sm:text-[11px] text-gray-400 flex-wrap">
              <span className="flex items-center gap-1 bg-white/5 px-2.5 py-0.5 sm:py-1 rounded-full border border-white/5">
                <Music2 className="w-3 h-3 text-cyan-400" />
                Sonido original #CyberVibe
              </span>
              <span className="flex items-center gap-1 bg-white/5 px-2.5 py-0.5 sm:py-1 rounded-full border border-white/5">
                <VideoIcon className="w-3 h-3 text-pink-400" />
                1.4K Shorts creados
              </span>
            </div>
          </div>
        </div>

        {/* CONTADORES (SIGUIENDO, SEGUIDORES, ME GUSTA) */}
        <div className="flex items-center justify-around sm:justify-center gap-2 sm:gap-3 bg-[#131522] p-2.5 sm:p-3 rounded-2xl border border-white/5 shadow-inner w-full md:w-auto">
          <div className="text-center px-2 sm:px-4">
            <span className="block text-base sm:text-lg font-bold text-white">348</span>
            <span className="text-[9px] sm:text-[10px] uppercase tracking-wider text-gray-400 font-medium">Siguiendo</span>
          </div>
          <div className="w-px h-7 sm:h-8 bg-white/10"></div>
          <div className="text-center px-2 sm:px-4">
            <span className="block text-base sm:text-lg font-bold text-white">2.4M</span>
            <span className="text-[9px] sm:text-[10px] uppercase tracking-wider text-gray-400 font-medium">Seguidores</span>
          </div>
          <div className="w-px h-7 sm:h-8 bg-white/10"></div>
          <div className="text-center px-2 sm:px-4">
            <span className="block text-base sm:text-lg font-bold text-white">18.9M</span>
            <span className="text-[9px] sm:text-[10px] uppercase tracking-wider text-gray-400 font-medium">Me Gusta</span>
          </div>
        </div>

      </div>

      {/* BOTONES DE ACCION (Totalmente interactivos y adaptables a 2 columnas en movil) */}
      <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-2 sm:gap-3 pb-8 w-full">
        
        {/* Editar perfil */}
        <button
          onClick={() => setShowEditProfileModal(true)}
          className="flex items-center justify-center gap-1.5 px-4 py-2.5 sm:py-2 rounded-xl bg-gradient-to-r from-pink-600 to-purple-600 text-white text-xs font-semibold shadow-lg shadow-pink-500/20 hover:brightness-110 active:scale-95 transition-all"
        >
          <Pencil className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Editar perfil</span>
        </button>

        {/* Compartir perfil */}
        <button 
          type="button"
          onClick={() => setShowShareModal(true)}
          className="flex items-center justify-center gap-1.5 px-4 py-2.5 sm:py-2 rounded-xl bg-[#171926] hover:bg-[#202334] text-gray-300 hover:text-white text-xs font-semibold border border-white/5 active:scale-95 transition-all"
        >
          <Share2 className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Compartir perfil</span>
        </button>

        {/* Estadisticas de creador */}
        <button 
          type="button"
          onClick={() => setShowStatsModal(true)}
          className="flex items-center justify-center gap-1.5 px-4 py-2.5 sm:py-2 rounded-xl bg-[#171926] hover:bg-[#202334] text-gray-300 hover:text-white text-xs font-semibold border border-white/5 active:scale-95 transition-all"
        >
          <TrendingUp className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
          <span>Estadisticas</span>
        </button>

        {/* Configuracion */}
        <button 
          type="button"
          onClick={() => setShowSettingsModal(true)}
          aria-label="Configuracion"
          className="flex items-center justify-center gap-1.5 px-4 py-2.5 sm:py-2 rounded-xl bg-[#171926] hover:bg-[#202334] text-gray-400 hover:text-white border border-white/5 active:scale-95 transition-all"
        >
          <Settings className="w-3.5 h-3.5 flex-shrink-0" />
          <span className="sm:hidden text-xs font-semibold text-gray-300">Ajustes</span>
        </button>
      </div>

      {/* HISTORIAS DESTACADAS INTERACTIVAS */}
      <div className="pb-8">
        <div className="flex items-center justify-between pb-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-pink-500"></span>
            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-300">Historias Destacadas</h2>
          </div>
          <button className="text-xs text-gray-400 hover:text-white flex items-center gap-0.5">
            <span>Ver archivo</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-5 overflow-x-auto pb-2 scrollbar-none">
          {highlights.map((h, index) => (
            <div
              key={h.id}
              onClick={() => handleOpenStory(index)}
              className="flex flex-col items-center gap-1.5 group cursor-pointer flex-shrink-0"
            >
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full p-0.5 bg-gradient-to-tr from-purple-500 to-pink-500 group-hover:scale-105 transition-transform shadow-md">
                <img
                  src={h.image}
                  alt={h.title}
                  className="w-full h-full rounded-full object-cover border border-[#0c0d14]"
                />
              </div>
              <span className="text-[11px] text-gray-300 group-hover:text-white transition-colors">{h.title}</span>
            </div>
          ))}

          {/* Boton + Nuevo */}
          <div
            onClick={() => setShowNewStoryModal(true)}
            className="flex flex-col items-center gap-1.5 group cursor-pointer flex-shrink-0"
          >
            <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full border border-dashed border-gray-600 flex items-center justify-center bg-white/5 group-hover:border-pink-500 transition-colors">
              <Plus className="w-5 h-5 text-gray-400 group-hover:text-pink-400" />
            </div>
            <span className="text-[11px] text-gray-400 group-hover:text-white">Nuevo</span>
          </div>
        </div>
      </div>

      {/* PESTANAS DE CONTENIDO (Reels, Guardados, Borradores, Me Gusta) */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-6">
        <div className="flex items-center gap-4 sm:gap-8 text-xs font-semibold">
          
          {/* Reels 84 */}
          <button
            onClick={() => setActiveTab('reels')}
            className={`flex items-center gap-2 pb-1 relative transition-colors ${
              activeTab === 'reels' ? 'text-white' : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Film className="w-4 h-4" />
            <span>Reels</span>
            <span className="px-1.5 py-0.2 bg-white/10 text-[10px] rounded-full">84</span>
            {activeTab === 'reels' && (
              <span className="absolute -bottom-3 left-0 w-full h-0.5 bg-pink-500 shadow-sm shadow-pink-500"></span>
            )}
          </button>

          {/* Guardados 3 colecciones */}
          <button
            onClick={() => setActiveTab('saved')}
            className={`flex items-center gap-2 pb-1 relative transition-colors ${
              activeTab === 'saved' ? 'text-white' : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Bookmark className="w-4 h-4" />
            <span>Guardados</span>
            <span className="px-1.5 py-0.2 bg-white/10 text-[10px] rounded-full">3 colecciones</span>
            {activeTab === 'saved' && (
              <span className="absolute -bottom-3 left-0 w-full h-0.5 bg-pink-500 shadow-sm shadow-pink-500"></span>
            )}
          </button>

          {/* Borradores 4 activos */}
          <button
            onClick={() => setActiveTab('drafts')}
            className={`flex items-center gap-2 pb-1 relative transition-colors ${
              activeTab === 'drafts' ? 'text-white' : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Archive className="w-4 h-4" />
            <span>Borradores</span>
            <span className="px-1.5 py-0.2 bg-pink-600/30 text-pink-300 text-[10px] rounded-full">4 activos</span>
            {activeTab === 'drafts' && (
              <span className="absolute -bottom-3 left-0 w-full h-0.5 bg-pink-500 shadow-sm shadow-pink-500"></span>
            )}
          </button>

          {/* Me Gusta (Con candado de privacidad) */}
          <button
            onClick={() => setActiveTab('liked')}
            className={`flex items-center gap-1.5 pb-1 relative transition-colors ${
              activeTab === 'liked' ? 'text-white' : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            <Heart className="w-4 h-4" />
            <span>Me Gusta</span>
            <Lock className="w-3 h-3 text-gray-500" />
            {activeTab === 'liked' && (
              <span className="absolute -bottom-3 left-0 w-full h-0.5 bg-pink-500 shadow-sm shadow-pink-500"></span>
            )}
          </button>
        </div>

        <div className="flex items-center gap-1 text-gray-400">
          <button className="p-1.5 rounded hover:text-white hover:bg-white/5 transition-colors text-white">
            <Grid className="w-4 h-4" />
          </button>
          <button className="p-1.5 rounded hover:text-white hover:bg-white/5 transition-colors">
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* CONTENIDO SEGUN LA PESTANA ACTIVA */}
      
      {/* 1. TAB REELS (8 VIDEOS) */}
      {activeTab === 'reels' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {reelsVideos.map((v) => (
            <div
              key={v.id}
              onClick={() => setSelectedVideo(v)}
              className="group relative aspect-[9/16] rounded-2xl overflow-hidden bg-[#131522] border border-white/5 hover:border-pink-500/40 cursor-pointer shadow-lg transition-all hover:scale-[1.02]"
            >
              <img
                src={v.image}
                alt={v.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none"></div>

              {v.isPinned && (
                <div className="absolute top-2.5 left-2.5 px-2 py-0.5 rounded-full bg-pink-600/90 text-white text-[9px] font-bold tracking-wider flex items-center gap-1 backdrop-blur-sm shadow">
                  <span>Fijado</span>
                  <span className="text-pink-200">· Perfil de Usuario y Contenido</span>
                </div>
              )}

              {v.hasAudioNote && (
                <div className="absolute top-2.5 right-2.5 w-6 h-6 rounded-full bg-black/60 flex items-center justify-center text-white backdrop-blur-sm">
                  <Music2 className="w-3 h-3 text-cyan-400" />
                </div>
              )}

              <div className="absolute bottom-3 left-3 right-3 text-white">
                <h3 className="text-xs font-semibold line-clamp-2 leading-tight group-hover:text-pink-300 transition-colors">
                  {v.title}
                </h3>
                <div className="flex items-center justify-between mt-2 text-[10px] text-gray-300">
                  <span className="flex items-center gap-1">
                    <Play className="w-3 h-3 fill-white text-white" />
                    {v.views}
                  </span>
                  <span className="flex items-center gap-1">
                    <Heart className="w-3 h-3 text-rose-400 fill-rose-400" />
                    {v.likes}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 2. TAB GUARDADOS (3 COLECCIONES) */}
      {activeTab === 'saved' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Tus colecciones privadas y referencias guardadas</span>
            <button className="text-cyan-400 hover:underline flex items-center gap-1">
              <Plus className="w-3.5 h-3.5" />
              <span>Nueva Coleccion</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {savedCollections.map((col) => (
              <div
                key={col.id}
                className="p-3.5 rounded-2xl bg-[#141524] border border-white/5 hover:border-cyan-500/30 transition-all cursor-pointer group"
              >
                <div className="relative aspect-video rounded-xl overflow-hidden bg-black mb-3">
                  <img src={col.cover} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                    <Folder className="w-8 h-8 text-white/80 group-hover:scale-110 transition-transform" />
                  </div>
                  <span className="absolute bottom-2 right-2 px-2 py-0.5 rounded-md bg-black/70 text-white font-mono text-[10px]">
                    {col.count} videos
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                  {col.title}
                </h4>
                <span className="text-[10px] text-gray-500">Coleccion personal</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. TAB BORRADORES (4 ACTIVOS) */}
      {activeTab === 'drafts' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Borradores pendientes de publicacion en Creator Studio</span>
            <span className="text-pink-400 font-mono text-[11px]">4 borradores sincronizados</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {draftVideos.map((d) => (
              <div
                key={d.id}
                className="p-3 rounded-2xl bg-[#141524] border border-white/5 hover:border-pink-500/40 flex flex-col justify-between transition-all"
              >
                <div className="relative aspect-[9/14] rounded-xl overflow-hidden bg-black mb-2.5">
                  <img src={d.image} alt="" className="w-full h-full object-cover opacity-80" />
                  <span className="absolute top-2 left-2 px-2 py-0.5 rounded bg-pink-600 text-white font-bold text-[9px] uppercase">
                    Borrador
                  </span>
                  <span className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/70 text-white font-mono text-[9px]">
                    {d.duration}
                  </span>
                </div>

                <div className="space-y-2 flex-1 flex flex-col justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-white line-clamp-2 leading-tight">{d.title}</h4>
                    <span className="text-[10px] text-gray-500 block pt-0.5">{d.modified}</span>
                  </div>

                  <button
                    onClick={() => navigate('/estudio')}
                    className="w-full py-1.5 rounded-xl bg-white/10 hover:bg-pink-600 text-gray-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <span>Editar en Estudio</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. TAB ME GUSTA (PRIVADO) */}
      {activeTab === 'liked' && (
        <div className="space-y-4">
          <div className="p-3.5 rounded-2xl bg-[#18192a] border border-white/10 flex items-center gap-3 text-xs text-gray-300">
            <Lock className="w-4 h-4 text-pink-400 flex-shrink-0" />
            <span>Tus videos favoritos solo son visibles para ti. Nadie mas puede ver esta lista.</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {reelsVideos.slice(0, 4).map((v) => (
              <div
                key={v.id}
                onClick={() => setSelectedVideo(v)}
                className="group relative aspect-[9/16] rounded-2xl overflow-hidden bg-[#131522] border border-white/5 cursor-pointer"
              >
                <img src={v.image} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                <div className="absolute bottom-3 left-3 right-3 text-white">
                  <h4 className="text-xs font-semibold line-clamp-1">{v.title}</h4>
                  <span className="text-[10px] text-rose-400 flex items-center gap-1 mt-1">
                    <Heart className="w-3 h-3 fill-rose-400" />
                    Favorito
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MODAL 1: EDITAR PERFIL */}
      {showEditProfileModal && (
        <div
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setShowEditProfileModal(false)}
        >
          <div
            className="relative w-full max-w-lg rounded-3xl bg-[#141524] border border-white/10 shadow-2xl p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Pencil className="w-4 h-4 text-pink-400" />
                <span>Editar Informacion del Perfil</span>
              </h3>
              <button onClick={() => setShowEditProfileModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs text-gray-300 font-medium">Nombre Completo</label>
                <input
                  type="text"
                  value={profileData.fullName}
                  onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-pink-500/50"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-gray-300 font-medium">Nombre de Usuario (@)</label>
                <input
                  type="text"
                  value={profileData.username}
                  onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-pink-500/50"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-gray-300 font-medium">Biografia y Metadatos</label>
                <textarea
                  rows={3}
                  value={profileData.bio}
                  onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-pink-500/50 leading-relaxed resize-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs text-gray-300 font-medium">Email de Colaboraciones</label>
                  <input
                    type="email"
                    value={profileData.emailCollab}
                    onChange={(e) => setProfileData({ ...profileData, emailCollab: e.target.value })}
                    className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-pink-500/50"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-gray-300 font-medium">Ubicacion</label>
                  <input
                    type="text"
                    value={profileData.city}
                    onChange={(e) => setProfileData({ ...profileData, city: e.target.value })}
                    className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-pink-500/50"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEditProfileModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-gray-300"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold shadow-md shadow-pink-500/20"
                >
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: COMPARTIR PERFIL */}
      {showShareModal && (
        <div
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setShowShareModal(false)}
        >
          <div
            className="relative w-full max-w-sm rounded-3xl bg-[#141524] border border-white/10 shadow-2xl p-6 space-y-5 text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Share2 className="w-4 h-4 text-cyan-400" />
                <span>Compartir Perfil</span>
              </h3>
              <button onClick={() => setShowShareModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Codigo de Perfil QR / Avatar */}
            <div className="p-4 rounded-2xl bg-gradient-to-b from-purple-900/40 to-pink-900/30 border border-white/10 flex flex-col items-center gap-2">
              <img src={profileData.avatar} alt="" className="w-16 h-16 rounded-full border-2 border-pink-500 object-cover" />
              <span className="text-sm font-bold text-white">{profileData.fullName}</span>
              <span className="text-xs text-cyan-400 font-mono">follow.tv/@{profileData.username}</span>
            </div>

            {/* Enlace y boton de copiar */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 bg-[#1b1c2e] p-2 rounded-xl border border-white/10 text-xs">
                <span className="text-gray-400 truncate flex-1 text-left">https://follow.tv/@valeria_creatrix</span>
                <button
                  onClick={handleCopyProfileLink}
                  className="px-3 py-1.5 rounded-lg bg-pink-600 hover:bg-pink-500 text-white font-bold flex items-center gap-1 transition-colors"
                >
                  {copiedLink ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedLink ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: ESTADISTICAS DE CREADOR */}
      {showStatsModal && (
        <div
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setShowStatsModal(false)}
        >
          <div
            className="relative w-full max-w-lg rounded-3xl bg-[#141524] border border-white/10 shadow-2xl p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2 text-cyan-400">
                <TrendingUp className="w-4 h-4" />
                <h3 className="text-sm font-bold text-white">Estadisticas de Creador</h3>
              </div>
              <button onClick={() => setShowStatsModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Metricas Principales */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3.5 rounded-2xl bg-[#1a1c2e] border border-white/5 text-center">
                <span className="text-xs text-gray-400 font-medium block">Total Views</span>
                <span className="text-lg font-black text-white font-mono mt-0.5 block">18.9M</span>
                <span className="text-[10px] text-cyan-400 font-semibold">+28.4% este mes</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#1a1c2e] border border-white/5 text-center">
                <span className="text-xs text-gray-400 font-medium block">Seguidores</span>
                <span className="text-lg font-black text-white font-mono mt-0.5 block">2.4M</span>
                <span className="text-[10px] text-pink-400 font-semibold">+48K nuevos</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#1a1c2e] border border-white/5 text-center">
                <span className="text-xs text-gray-400 font-medium block">Interaccion</span>
                <span className="text-lg font-black text-white font-mono mt-0.5 block">8.4%</span>
                <span className="text-[10px] text-emerald-400 font-semibold">Alta retencion</span>
              </div>
            </div>

            {/* Distribucion Demografica */}
            <div className="p-4 rounded-2xl bg-[#1a1c2e] border border-white/5 space-y-2 text-xs">
              <span className="text-gray-300 font-bold block">Paises Principales de Audiencia:</span>
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-gray-400">
                  <span>Espana (Madrid, Barcelona)</span>
                  <span className="font-mono text-white">48%</span>
                </div>
                <div className="flex items-center justify-between text-gray-400">
                  <span>Japon (Tokyo, Osaka)</span>
                  <span className="font-mono text-white">26%</span>
                </div>
                <div className="flex items-center justify-between text-gray-400">
                  <span>Mexico & Latinoamerica</span>
                  <span className="font-mono text-white">14%</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => {
                setShowStatsModal(false);
                navigate('/estudio');
              }}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-xs shadow-md shadow-pink-500/20"
            >
              Ver Metricas Privadas en Creator Studio
            </button>
          </div>
        </div>
      )}

      {/* MODAL 4: AJUSTES Y CONFIGURACION FUNCIONAL COMPLETA (SETTINGS) */}
      <SettingsModal
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
      />

      {/* VISOR MODAL DE HISTORIAS DESTACADAS (STORIES VIEWER) */}
      {activeStoryIndex !== null && (
        <div
          className="fixed inset-0 z-50 bg-black/95 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setActiveStoryIndex(null)}
        >
          <div
            className="relative w-full max-w-sm aspect-[9/16] rounded-3xl overflow-hidden bg-[#12131e] border border-white/10 shadow-2xl flex flex-col justify-between p-4"
            onClick={(e) => e.stopPropagation()}
            onMouseDown={() => setIsStoryPaused(true)}
            onMouseUp={() => setIsStoryPaused(false)}
            onTouchStart={() => setIsStoryPaused(true)}
            onTouchEnd={() => setIsStoryPaused(false)}
          >
            <img
              src={highlights[activeStoryIndex].image}
              alt=""
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-transparent to-black/80 pointer-events-none"></div>

            <div className="relative z-10 flex items-center gap-1.5 w-full pt-1">
              {highlights.map((_, idx) => (
                <div key={idx} className="flex-1 h-1 rounded-full bg-white/25 overflow-hidden">
                  <div
                    className="h-full bg-white transition-all duration-100 rounded-full"
                    style={{
                      width:
                        idx < activeStoryIndex
                          ? '100%'
                          : idx === activeStoryIndex
                          ? `${storyProgress}%`
                          : '0%',
                    }}
                  ></div>
                </div>
              ))}
            </div>

            <div className="relative z-10 flex items-center justify-between pt-2">
              <div className="flex items-center gap-2.5">
                <img
                  src={profileData.avatar}
                  alt={profileData.fullName}
                  className="w-9 h-9 rounded-full border border-pink-500 object-cover"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-white">{profileData.username}</span>
                    <CheckCircle className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />
                  </div>
                  <span className="text-[10px] text-pink-300 font-medium">
                    {highlights[activeStoryIndex].title} • {highlights[activeStoryIndex].date}
                  </span>
                </div>
              </div>

              <button
                onClick={() => setActiveStoryIndex(null)}
                className="p-1.5 rounded-full bg-black/50 text-white hover:bg-black/70"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={() => {
                if (activeStoryIndex > 0) {
                  setActiveStoryIndex(activeStoryIndex - 1);
                  setStoryProgress(0);
                }
              }}
              disabled={activeStoryIndex === 0}
              className="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/40 text-white hover:bg-black/60 disabled:opacity-0 transition-opacity z-10"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <button
              onClick={() => {
                if (activeStoryIndex < highlights.length - 1) {
                  setActiveStoryIndex(activeStoryIndex + 1);
                  setStoryProgress(0);
                } else {
                  setActiveStoryIndex(null);
                }
              }}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/40 text-white hover:bg-black/60 z-10"
            >
              <ChevronRight className="w-5 h-5" />
            </button>

            <div className="relative z-10 flex items-center gap-2 pt-2">
              <input
                type="text"
                placeholder="Enviar mensaje a Valeria..."
                className="flex-1 bg-black/50 border border-white/20 rounded-full px-4 py-2 text-xs text-white placeholder-gray-400 focus:outline-none focus:border-pink-500"
              />
              <button className="p-2 rounded-full bg-rose-500/30 text-rose-400 border border-rose-500/40">
                <Heart className="w-4 h-4 fill-rose-400" />
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL NUEVA HISTORIA DESTACADA */}
      {showNewStoryModal && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setShowNewStoryModal(false)}
        >
          <div
            className="relative w-full max-w-md rounded-3xl bg-[#141524] border border-white/10 shadow-2xl p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-pink-400" />
                <h3 className="text-sm font-bold text-white">Nueva Historia Destacada</h3>
              </div>
              <button
                onClick={() => setShowNewStoryModal(false)}
                className="p-1 rounded-full text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (!newStoryTitle.trim()) return;
                setHighlights([...highlights, { id: Date.now().toString(), title: newStoryTitle.trim(), image: newStoryImage, date: "Hoy" }]);
                setNewStoryTitle('');
                setShowNewStoryModal(false);
              }}
              className="space-y-4"
            >
              <div className="space-y-1.5">
                <label className="text-xs text-gray-300 font-medium">Titulo del album / coleccion</label>
                <input
                  type="text"
                  value={newStoryTitle}
                  onChange={(e) => setNewStoryTitle(e.target.value)}
                  placeholder="Ej: Setup 2026, Tokyo Street, etc."
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs text-gray-300 font-medium block">Foto de portada</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300',
                    'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=300',
                    'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300'
                  ].map((imgUrl, i) => (
                    <img
                      key={i}
                      src={imgUrl}
                      alt=""
                      onClick={() => setNewStoryImage(imgUrl)}
                      className={`aspect-square rounded-xl object-cover cursor-pointer border-2 transition-all ${
                        newStoryImage === imgUrl ? 'border-pink-500 scale-105' : 'border-white/5 opacity-60'
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewStoryModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-gray-300 font-semibold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold shadow-md shadow-pink-500/20"
                >
                  Crear Historia
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL DE PREVISUALIZACION DE VIDEO PROFESIONAL (ESTILO TIKTOK/REELS) */}
      {selectedVideo && (
        <div 
          className="fixed inset-0 z-50 bg-black/95 backdrop-blur-md flex items-center justify-center p-2 sm:p-4 animate-in fade-in duration-200"
          onClick={() => setSelectedVideo(null)}
        >
          {/* Botones de navegacion lateral en escritorio */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
              const prevIndex = (currentIndex - 1 + reelsVideos.length) % reelsVideos.length;
              setSelectedVideo(reelsVideos[prevIndex]);
            }}
            className="hidden md:flex absolute left-8 top-1/2 -translate-y-1/2 p-3.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all border border-white/10 z-20 shadow-xl hover:scale-105"
            title="Video anterior (Flecha izquierda)"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              const currentIndex = reelsVideos.findIndex(v => v.id === selectedVideo.id);
              const nextIndex = (currentIndex + 1) % reelsVideos.length;
              setSelectedVideo(reelsVideos[nextIndex]);
            }}
            className="hidden md:flex absolute right-8 top-1/2 -translate-y-1/2 p-3.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all border border-white/10 z-20 shadow-xl hover:scale-105"
            title="Siguiente video (Flecha derecha)"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          <div 
            onTouchStart={handleModalTouchStart}
            onTouchEnd={handleModalTouchEnd}
            className="relative max-w-sm w-full aspect-[9/16] h-[calc(100dvh-5rem)] max-h-[88dvh] rounded-2xl sm:rounded-[28px] overflow-hidden bg-black border border-white/15 shadow-2xl select-none"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Reproductor de Video con fallback garantizado a poster de alta definicion */}
            <video
              ref={modalVideoRef}
              src={selectedVideo.videoUrl}
              poster={selectedVideo.image}
              autoPlay
              loop
              muted={isVideoMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover cursor-pointer"
              onClick={() => {
                if (modalVideoRef.current) {
                  if (modalVideoRef.current.paused) {
                    modalVideoRef.current.play();
                    setIsVideoPlaying(true);
                  } else {
                    modalVideoRef.current.pause();
                    setIsVideoPlaying(false);
                  }
                }
              }}
              onTimeUpdate={() => {
                if (modalVideoRef.current && modalVideoRef.current.duration) {
                  const pct = (modalVideoRef.current.currentTime / modalVideoRef.current.duration) * 100;
                  setModalVideoProgress(pct);
                }
              }}
            />

            {/* Icono de pausa flotante cuando esta pausado */}
            {!isVideoPlaying && (
              <div 
                onClick={() => {
                  if (modalVideoRef.current) {
                    modalVideoRef.current.play();
                    setIsVideoPlaying(true);
                  }
                }}
                className="absolute inset-0 flex items-center justify-center bg-black/30 z-10 cursor-pointer pointer-events-auto"
              >
                <div className="w-16 h-16 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center border border-white/20 text-white shadow-xl hover:scale-110 transition-transform">
                  <Play className="w-8 h-8 fill-white ml-1" />
                </div>
              </div>
            )}

            {/* Gradientes cinematograficos para contraste optimo */}
            <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-black/85 via-black/30 to-transparent pointer-events-none z-10"></div>
            <div className="absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-black/95 via-black/60 to-transparent pointer-events-none z-10"></div>

            {/* Cabecera superior anclada arriba */}
            <div className="absolute top-0 inset-x-0 z-20 flex items-center justify-between p-4">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-black/60 backdrop-blur-md text-[10px] font-bold tracking-wider text-white border border-white/10 uppercase">
                  4K HDR · Follow
                </span>
                <button
                  onClick={() => setIsVideoMuted(!isVideoMuted)}
                  className="p-1.5 rounded-full bg-black/60 backdrop-blur-md text-white hover:bg-black/80 transition-colors border border-white/10 flex items-center gap-1.5 px-2.5 text-[10px] font-medium"
                >
                  {isVideoMuted ? (
                    <>
                      <VolumeX className="w-3.5 h-3.5 text-pink-400" />
                      <span>Silenciado</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Sonido activo</span>
                    </>
                  )}
                </button>
              </div>

              <button
                onClick={() => setSelectedVideo(null)}
                className="p-2 rounded-full bg-black/60 backdrop-blur-md text-gray-300 hover:text-white hover:bg-black/80 transition-all border border-white/10"
                title="Cerrar visor (Escape)"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Barra lateral de acciones sociales (derecha) */}
            <div className="absolute right-3 bottom-14 z-20 flex flex-col items-center gap-3">
              {/* Avatar creador con boton seguir */}
              <div className="relative mb-1">
                <img
                  src={profileData.avatar}
                  alt={profileData.fullName}
                  className="w-10 h-10 rounded-full object-cover border-2 border-pink-500 shadow-md"
                />
                <button
                  onClick={() => setIsFollowing(!isFollowing)}
                  className={`absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold shadow ${
                    isFollowing ? 'bg-cyan-500 text-black' : 'bg-pink-600 text-white'
                  }`}
                >
                  {isFollowing ? <Check className="w-2.5 h-2.5" /> : <Plus className="w-2.5 h-2.5" />}
                </button>
              </div>

              {/* Me Gusta */}
              <button
                onClick={() => {
                  setModalLikedMap(prev => ({ ...prev, [selectedVideo.id]: !prev[selectedVideo.id] }));
                }}
                className="flex flex-col items-center gap-0.5 group"
              >
                <div className={`p-2.5 rounded-full backdrop-blur-md border transition-transform group-hover:scale-110 ${
                  modalLikedMap[selectedVideo.id]
                    ? 'bg-rose-500/30 text-rose-400 border-rose-500/40'
                    : 'bg-black/50 text-white border-white/10 hover:bg-black/70'
                }`}>
                  <Heart className={`w-5 h-5 ${modalLikedMap[selectedVideo.id] ? 'fill-rose-400 text-rose-400' : ''}`} />
                </div>
                <span className="text-[10px] font-bold text-white shadow-sm">
                  {modalLikedMap[selectedVideo.id] ? '411K' : selectedVideo.likes}
                </span>
              </button>

              {/* Comentarios */}
              <button className="flex flex-col items-center gap-0.5 group">
                <div className="p-2.5 rounded-full bg-black/50 backdrop-blur-md text-white border border-white/10 hover:bg-black/70 transition-transform group-hover:scale-110">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-bold text-white shadow-sm">1.4K</span>
              </button>

              {/* Guardar en coleccion */}
              <button
                onClick={() => {
                  setModalBookmarksMap(prev => ({ ...prev, [selectedVideo.id]: !prev[selectedVideo.id] }));
                }}
                className="flex flex-col items-center gap-0.5 group"
              >
                <div className={`p-2.5 rounded-full backdrop-blur-md border transition-transform group-hover:scale-110 ${
                  modalBookmarksMap[selectedVideo.id]
                    ? 'bg-yellow-500/30 text-yellow-400 border-yellow-500/40'
                    : 'bg-black/50 text-white border-white/10 hover:bg-black/70'
                }`}>
                  <Bookmark className={`w-5 h-5 ${modalBookmarksMap[selectedVideo.id] ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                </div>
                <span className="text-[10px] font-bold text-white shadow-sm">Guardar</span>
              </button>

              {/* Compartir */}
              <button
                onClick={() => {
                  handleCopyProfileLink();
                }}
                className="flex flex-col items-center gap-0.5 group"
              >
                <div className="p-2.5 rounded-full bg-black/50 backdrop-blur-md text-white border border-white/10 hover:bg-black/70 transition-transform group-hover:scale-110">
                  <Share2 className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-bold text-white shadow-sm">
                  {copiedLink ? 'Copiado' : 'Compartir'}
                </span>
              </button>

              {/* Disco de musica girando */}
              <div className="w-8 h-8 rounded-full bg-black/80 border border-white/20 p-1 flex items-center justify-center animate-spin-slow">
                <Music2 className="w-4 h-4 text-cyan-400" />
              </div>
            </div>

            {/* Informacion del video anclada estrictamente a la zona inferior izquierda */}
            <div className="absolute left-0 bottom-2.5 right-16 z-20 p-4 space-y-1.5 select-text pointer-events-none">
              <div className="flex items-center gap-1.5 pointer-events-auto">
                <span className="text-xs font-bold text-white drop-shadow">@{profileData.username}</span>
                <CheckCircle className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />
                <span className="text-[9px] font-semibold text-gray-300 drop-shadow">· 2d</span>
              </div>

              <h3 className="text-xs font-bold text-white line-clamp-1 drop-shadow pointer-events-auto">{selectedVideo.title}</h3>
              {selectedVideo.description && (
                <p className="text-[11px] text-gray-200 line-clamp-2 leading-relaxed drop-shadow pointer-events-auto">
                  {selectedVideo.description}
                </p>
              )}

              {selectedVideo.tags && (
                <div className="flex items-center gap-1 flex-wrap pt-0.5 pointer-events-auto">
                  {selectedVideo.tags.map(tag => (
                    <span key={tag} className="text-[10px] font-semibold text-pink-400 hover:underline cursor-pointer drop-shadow">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center gap-1.5 text-[11px] text-gray-200 pt-0.5 drop-shadow pointer-events-auto">
                <Music2 className="w-3.5 h-3.5 text-cyan-400 animate-pulse flex-shrink-0" />
                <span className="truncate">{selectedVideo.soundTitle || 'Original Sound - Valeria Studio'}</span>
              </div>
            </div>

            {/* Barra de progreso de reproduccion en el borde inferior absoluto */}
            <div className="absolute bottom-0 inset-x-0 z-30 w-full h-1 bg-white/20">
              <div 
                className="h-full bg-gradient-to-r from-pink-500 to-purple-500 transition-all duration-100"
                style={{ width: `${modalVideoProgress}%` }}
              ></div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
