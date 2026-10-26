/**
 * Pantalla 4: Feed Principal Para Ti (Follow Home Feed).
 * Replicación exacta del diseño de Stitch con reproductor de video interactivo,
 * soporte de atajos de teclado (Siguiente, Like, Mute) y panel de comentarios reactivo.
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Heart, MessageSquare, Bookmark, Share2, Sparkles, 
  Volume2, VolumeX, MoreVertical, CheckCircle, Plus, 
  Music, Radio, ArrowUp, ArrowDown, Send, CornerDownRight, 
  SlidersHorizontal, X, Pin, Flame, Smile, Trophy, Wand2
} from 'lucide-react';
import { getForYouFeed, getVideoComments, postVideoComment, toggleLikeVideo, toggleBookmarkVideo } from '../services/api';
import { Video, Comment } from '../types';

export const FeedPage: React.FC = () => {
  const [feedTab, setFeedTab] = useState<'following' | 'foryou' | 'live'>('foryou');
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(1200000);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarksCount, setBookmarksCount] = useState(120000);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newCommentText, setNewCommentText] = useState('');
  const [showComments, setShowComments] = useState(true);
  const [isFollowingCreator, setIsFollowingCreator] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const touchStartY = useRef<number | null>(null);

  // Soporte para gestos táctiles de deslizamiento (Swipe Up / Down) en dispositivos móviles
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartY.current === null) return;
    const touchEndY = e.changedTouches[0].clientY;
    const diff = touchStartY.current - touchEndY;
    // Umbral de 45px para cambiar de video mediante gesto natural de swipe
    if (diff > 45) {
      // Deslizar hacia arriba -> Siguiente video
      setCurrentIndex((prev) => (prev + 1) % (videos.length || 1));
    } else if (diff < -45) {
      // Deslizar hacia abajo -> Video anterior
      setCurrentIndex((prev) => (prev - 1 + (videos.length || 1)) % (videos.length || 1));
    }
    touchStartY.current = null;
  };

  // Cargar feed de videos inicial
  useEffect(() => {
    const fetchFeed = async () => {
      const data = await getForYouFeed();
      setVideos(data);
      if (data.length > 0) {
        setLikesCount(data[0].likes_count);
        const comms = await getVideoComments(data[0].id);
        setComments(comms);
      }
    };
    fetchFeed();
  }, []);

  // Controladores de atajos de teclado ISO 25010 (Usabilidad y ergonomía)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setCurrentIndex((prev) => (prev + 1) % (videos.length || 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setCurrentIndex((prev) => (prev - 1 + (videos.length || 1)) % (videos.length || 1));
      } else if (e.key.toLowerCase() === 'l') {
        e.preventDefault();
        handleLikeToggle();
      } else if (e.key.toLowerCase() === 'm') {
        e.preventDefault();
        setIsMuted((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [videos, isLiked]);

  const handleLikeToggle = () => {
    setIsLiked((prev) => {
      const next = !prev;
      setLikesCount((c) => (next ? c + 1 : c - 1));
      return next;
    });
    if (videos[currentIndex]) {
      toggleLikeVideo(videos[currentIndex].id);
    }
  };

  const handleBookmarkToggle = () => {
    setIsBookmarked((prev) => {
      const next = !prev;
      setBookmarksCount((c) => (next ? c + 1 : c - 1));
      return next;
    });
    if (videos[currentIndex]) {
      toggleBookmarkVideo(videos[currentIndex].id);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCommentText.trim()) return;
    const currentVideoId = videos[currentIndex]?.id || 1;
    const added = await postVideoComment(currentVideoId, newCommentText.trim());
    setComments((prev) => [added, ...prev]);
    setNewCommentText('');
  };

  const currentVideo = videos[currentIndex] || {
    id: 1,
    title: 'Configurando el nuevo setup holográfico para streaming nocturno',
    description: 'Configurando el nuevo setup holográfico para streaming nocturno. ¿Qué opinan de esta... #aesthetic #techtrends #creativelife #cyberpunk',
    video_url: '/videos/cyber_street.mp4',
    author: {
      username: 'valeria_creatrix',
      full_name: 'Valeria Gómez',
      avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'
    }
  };

  // Renderizado unificado de comentarios para panel de escritorio y bottom-sheet móvil
  const renderCommentsContent = () => (
    <>
      {/* Cabecera de Comentarios */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-pink-400" />
          <h3 className="text-xs font-bold text-white">Comentarios</h3>
          <span className="text-xs text-gray-400 font-mono">34,812</span>
        </div>

        <div className="flex items-center gap-1 text-gray-400">
          <button className="p-1 rounded hover:text-white transition-colors">
            <SlidersHorizontal className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => setShowComments(false)} className="p-1.5 rounded-full hover:bg-white/10 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Lista de Comentarios Scrollable */}
      <div className="flex-1 overflow-y-auto py-3 space-y-4 pr-1 min-h-[160px] max-h-[48vh] lg:max-h-[380px]">
        {comments.map((c) => {
          const commentAuthor = c.user || (c as any).author || {
            username: 'usuario',
            avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100',
            is_verified: false
          };
          const likesFormatted = typeof c.likes_count === 'number' ? c.likes_count.toLocaleString() : '0';
          return (
            <div key={c.id} className="space-y-1 text-xs">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <img 
                    src={commentAuthor.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'} 
                    alt={commentAuthor.username || 'Usuario'} 
                    className="w-7 h-7 rounded-full object-cover flex-shrink-0" 
                  />
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-white">{commentAuthor.username || 'usuario'}</span>
                      {commentAuthor.is_verified && <CheckCircle className="w-3 h-3 text-cyan-400 inline" />}
                      {c.is_pinned && (
                        <span className="text-[9px] font-extrabold uppercase px-1.5 bg-pink-600/30 text-pink-300 rounded border border-pink-500/30">
                          CREADOR
                        </span>
                      )}
                      <span className="text-[10px] text-gray-500 ml-1">{c.created_at || 'Reciente'}</span>
                    </div>
                    <p className="text-gray-200 text-xs mt-1 leading-snug">{c.content}</p>

                    <div className="flex items-center gap-3 mt-1.5 text-[10px] text-gray-400">
                      {c.is_pinned && (
                        <span className="flex items-center gap-1 text-pink-400 font-semibold">
                          <Pin className="w-3 h-3" />
                          Fijado
                        </span>
                      )}
                      <button className="hover:text-white font-medium">Responder</button>
                    </div>
                  </div>
                </div>

                {/* Likes del comentario */}
                <button className="flex flex-col items-center text-gray-400 hover:text-rose-400 flex-shrink-0">
                  <Heart className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-mono">{likesFormatted}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Reacciones Rápidas con Iconos Profesionales Lucide */}
      <div className="py-2 border-t border-white/5 flex items-center justify-between text-gray-400">
        <button className="p-1 hover:text-rose-400 hover:scale-110 transition-all"><Heart className="w-4 h-4 fill-rose-500/20" /></button>
        <button className="p-1 hover:text-amber-400 hover:scale-110 transition-all"><Flame className="w-4 h-4" /></button>
        <button className="p-1 hover:text-yellow-400 hover:scale-110 transition-all"><Trophy className="w-4 h-4" /></button>
        <button className="p-1 hover:text-cyan-400 hover:scale-110 transition-all"><Sparkles className="w-4 h-4" /></button>
        <button className="p-1 hover:text-purple-400 hover:scale-110 transition-all"><Wand2 className="w-4 h-4" /></button>
        <button className="p-1 hover:text-pink-400 hover:scale-110 transition-all"><Smile className="w-4 h-4" /></button>
      </div>

      {/* Formulario de Entrada de Comentario */}
      <form onSubmit={handleCommentSubmit} className="relative pt-1">
        <input
          type="text"
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
          placeholder="Añade un comentario para Valeria..."
          className="w-full bg-[#1c1e2f] border border-white/10 rounded-2xl pl-4 pr-11 py-2.5 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50"
        />
        <button
          type="submit"
          disabled={!newCommentText.trim()}
          className="absolute right-1.5 top-2.5 p-1.5 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white disabled:opacity-40 transition-opacity"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </>
  );

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-2 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* SUB-BARRA DE NAVEGACIÓN DEL FEED (Siguiendo / Para ti / En Directo + Atajos) */}
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex items-center gap-6 text-sm font-semibold">
          <button
            onClick={() => setFeedTab('following')}
            className={`transition-colors ${
              feedTab === 'following' ? 'text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Siguiendo
          </button>

          <button
            onClick={() => setFeedTab('foryou')}
            className={`flex items-center gap-1.5 transition-colors ${
              feedTab === 'foryou' ? 'text-white font-bold' : 'text-gray-400 hover:text-white'
            }`}
          >
            <span>Para ti</span>
            <span className="w-1.5 h-1.5 rounded-full bg-pink-500 shadow-sm shadow-pink-500"></span>
          </button>

          <button
            onClick={() => setFeedTab('live')}
            className={`flex items-center gap-1.5 transition-colors ${
              feedTab === 'live' ? 'text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Radio className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
            <span>En Directo</span>
          </button>
        </div>

        {/* Helper de Atajos de Teclado */}
        <div className="hidden md:flex items-center gap-2 text-[11px] text-gray-400 bg-[#161826] px-3 py-1 rounded-full border border-white/5 font-mono">
          <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-200">↑</kbd>
          <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-200">↓</kbd>
          <span className="text-gray-500">Siguiente</span>
          <span className="text-gray-600">/</span>
          <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-200">L</kbd>
          <span className="text-gray-500">Like</span>
          <span className="text-gray-600">/</span>
          <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-gray-200">M</kbd>
          <span className="text-gray-500">Silenciar</span>
        </div>
      </div>

      {/* CUERPO PRINCIPAL: TRES COLUMNAS (SIDEBAR IZQUIERDO, REEL CENTRAL, PANEL DE COMENTARIOS) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4 items-start">
        
        {/* COLUMNA IZQUIERDA (3 COLUMNAS): TENDENCIA, RECOMENDADOS Y ALCANCE */}
        <div className="hidden lg:block lg:col-span-3 space-y-4">
          
          {/* PISTA EN TENDENCIA */}
          <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                <Radio className="w-3.5 h-3.5" />
                <span>PISTA EN TENDENCIA</span>
              </div>
              <span className="text-gray-400 text-[10px] font-mono">#1 España</span>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-white flex-shrink-0 animate-spin-slow">
                <Music className="w-5 h-5" />
              </div>
              <div className="overflow-hidden">
                <h4 className="text-xs font-bold text-white truncate">Original Sound - Valeria ...</h4>
                <span className="text-[10px] text-gray-400">248.6K videos creados</span>
              </div>
            </div>

            <button className="w-full py-2 rounded-xl bg-[#1d2034] hover:bg-[#262a44] text-gray-200 text-xs font-semibold flex items-center justify-center gap-2 border border-white/5 transition-colors">
              <Bookmark className="w-3.5 h-3.5" />
              <span>Guardar audio</span>
            </button>
          </div>

          {/* RECOMENDADOS PARA TI */}
          <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white">Recomendados para ti</h3>
              <button className="text-[10px] text-cyan-400 hover:underline">Ver más</button>
            </div>

            <div className="space-y-3">
              {[
                { name: 'neo_kinetics', sub: '890K seguidores', img: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100' },
                { name: 'arch_lucas', sub: '412K seguidores', img: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100' },
                { name: 'synth_wave_lab', sub: '1.5M seguidores', img: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100' }
              ].map((rec) => (
                <div key={rec.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <img src={rec.img} alt="" className="w-8 h-8 rounded-full object-cover border border-white/10" />
                    <div>
                      <span className="text-xs font-semibold text-white block">{rec.name}</span>
                      <span className="text-[10px] text-gray-400 block">{rec.sub}</span>
                    </div>
                  </div>
                  <button className="px-3 py-1 rounded-xl bg-white/10 hover:bg-white/20 text-gray-200 text-[11px] font-semibold transition-colors">
                    Seguir
                  </button>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* COLUMNA CENTRAL (5 COLUMNAS): REPRODUCTOR VERTICAL TIKTOK/FOLLOW */}
        <div className="lg:col-span-5 flex justify-center w-full">
          <div 
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            className="relative w-full max-w-[400px] h-[calc(100dvh-8rem)] sm:h-auto sm:aspect-[9/16] rounded-2xl sm:rounded-[32px] overflow-hidden bg-black border border-white/10 shadow-2xl flex flex-col justify-between select-none"
          >
            
            {/* Elemento de video HTML5 real con Range / Streaming */}
            <video
              ref={videoRef}
              src={currentVideo.video_url}
              autoPlay
              loop
              muted={isMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover cursor-pointer"
              onClick={() => {
                if (videoRef.current) {
                  if (videoRef.current.paused) videoRef.current.play();
                  else videoRef.current.pause();
                }
              }}
            />

            {/* Gradientes para legibilidad superior e inferior */}
            <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-black/80 via-black/30 to-transparent pointer-events-none"></div>
            <div className="absolute inset-x-0 bottom-0 h-44 bg-gradient-to-t from-black/90 via-black/40 to-transparent pointer-events-none"></div>

            {/* CABECERA SUPERIOR DENTRO DEL REPRODUCTOR */}
            <div className="relative z-10 flex items-center justify-between p-4 text-xs">
              <span className="px-2.5 py-0.5 rounded-full bg-black/60 backdrop-blur-md text-[10px] font-bold tracking-wider text-white border border-white/10">
                4K HDR
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-2 rounded-full bg-black/50 backdrop-blur-md text-white hover:bg-black/70 transition-colors"
                >
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>
                <button className="p-2 rounded-full bg-black/50 backdrop-blur-md text-white hover:bg-black/70 transition-colors">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* ACCIONES FLOTANTES DERECHAS (LIKES, COMENTARIOS, BOOKMARK, SHARE, REMIX) */}
            <div className="absolute right-3.5 bottom-16 z-20 flex flex-col items-center gap-3">
              
              {/* Me Gusta */}
              <button onClick={handleLikeToggle} className="flex flex-col items-center gap-0.5 group">
                <div className={`p-2.5 rounded-full ${isLiked ? 'bg-rose-500/30 text-rose-400' : 'bg-black/50 text-white'} backdrop-blur-md group-hover:scale-110 transition-transform`}>
                  <Heart className={`w-6 h-6 ${isLiked ? 'fill-rose-500 text-rose-500' : ''}`} />
                </div>
                <span className="text-[11px] font-bold text-white drop-shadow">
                  {isLiked ? (likesCount >= 1000000 ? `${(likesCount / 1000000).toFixed(1)}M` : likesCount) : '1.2M'}
                </span>
              </button>

              {/* Comentarios */}
              <button onClick={() => setShowComments(!showComments)} className="flex flex-col items-center gap-0.5 group">
                <div className="p-2.5 rounded-full bg-black/50 text-white backdrop-blur-md group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <span className="text-[11px] font-bold text-white drop-shadow">34.8K</span>
              </button>

              {/* Guardados / Bookmarks */}
              <button onClick={handleBookmarkToggle} className="flex flex-col items-center gap-0.5 group">
                <div className={`p-2.5 rounded-full ${isBookmarked ? 'bg-yellow-500/30 text-yellow-400' : 'bg-black/50 text-white'} backdrop-blur-md group-hover:scale-110 transition-transform`}>
                  <Bookmark className={`w-6 h-6 ${isBookmarked ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                </div>
                <span className="text-[11px] font-bold text-white drop-shadow">120K</span>
              </button>

              {/* Compartir */}
              <button className="flex flex-col items-center gap-0.5 group">
                <div className="p-2.5 rounded-full bg-black/50 text-white backdrop-blur-md group-hover:scale-110 transition-transform">
                  <Share2 className="w-6 h-6" />
                </div>
                <span className="text-[11px] font-bold text-white drop-shadow">15.4K</span>
              </button>

              {/* Botón Remix */}
              <button className="flex flex-col items-center gap-0.5 group">
                <div className="p-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-pink-500/30 group-hover:scale-105 transition-transform">
                  <Wand2 className="w-5 h-5" />
                </div>
                <span className="text-[9px] font-bold text-pink-300">Remix</span>
              </button>

              {/* Disco de audio giratorio con avatar */}
              <div className="relative pt-1">
                <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-gray-900 to-gray-700 p-1 border border-white/20 animate-spin-slow">
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50"
                    alt=""
                    className="w-full h-full rounded-full object-cover"
                  />
                </div>
              </div>
            </div>

            {/* DETALLES DEL CREADOR Y DESCRIPCIÓN (SUPERPOSICIÓN INFERIOR) */}
            <div className="relative z-10 p-4 space-y-2 pr-16">
              
              {/* Creador y botón seguir */}
              <div className="flex items-center gap-2">
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100"
                  alt="Valeria Gómez"
                  className="w-8 h-8 rounded-full border border-pink-500 object-cover"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-white">valeria_creatrix</span>
                    <CheckCircle className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />
                    <button
                      onClick={() => setIsFollowingCreator(!isFollowingCreator)}
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full transition-all ${
                        isFollowingCreator
                          ? 'bg-white/20 text-gray-300'
                          : 'bg-pink-600 hover:bg-pink-500 text-white'
                      }`}
                    >
                      {isFollowingCreator ? 'Siguiendo' : '+ Seguir'}
                    </button>
                  </div>
                  <span className="text-[10px] text-gray-400 block -mt-0.5">Madrid • Diseñadora & Tech</span>
                </div>
              </div>

              {/* Descripción con hashtags */}
              <p className="text-xs text-gray-200 leading-snug line-clamp-3">
                {currentVideo.description}
              </p>

              {/* Ticker de Audio */}
              <div className="flex items-center gap-2 text-xs text-cyan-300">
                <Music className="w-3.5 h-3.5 flex-shrink-0 animate-bounce" />
                <span className="truncate text-[11px] font-medium">Original Sound - Valeria Studio • Sonido en...</span>
              </div>

              {/* Barra de Progreso del Video */}
              <div className="w-full bg-white/20 h-1 rounded-full overflow-hidden">
                <div className="w-1/2 h-full bg-pink-500 rounded-full"></div>
              </div>

            </div>

          </div>
        </div>

        {/* PANEL LATERAL DE COMENTARIOS (ESCRITORIO LG) */}
        {showComments && (
          <div className="hidden lg:flex lg:col-span-4 bg-[#141524] rounded-3xl border border-white/5 p-4 flex-col justify-between h-[560px]">
            {renderCommentsContent()}
          </div>
        )}

      </div>

      {/* MODAL BOTTOM SHEET DE COMENTARIOS (DISPOSITIVOS MOVILES) */}
      {showComments && (
        <div 
          className="lg:hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex flex-col justify-end animate-in fade-in duration-200"
          onClick={() => setShowComments(false)}
        >
          <div 
            className="bg-[#141524] rounded-t-3xl border-t border-white/10 p-4 max-h-[82dvh] flex flex-col justify-between shadow-2xl animate-in slide-in-from-bottom duration-250 pb-safe"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Tirador visual de arrastre superior */}
            <div className="w-12 h-1.5 bg-white/20 rounded-full mx-auto mb-3 flex-shrink-0 cursor-pointer" />
            {renderCommentsContent()}
          </div>
        </div>
      )}

    </div>
  );
};
