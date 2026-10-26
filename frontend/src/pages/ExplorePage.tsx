/**
 * Pantalla 3: Explorar, Búsqueda y Tendencias (Follow Explore).
 * Replicación exacta del diseño de Stitch con interactividad completa.
 */

import React, { useState } from 'react';
import { 
  Search, SlidersHorizontal, Users, Hash, Music, Radio, 
  X, CheckCircle, TrendingUp, Play, Pause, ChevronRight, 
  Flame, Heart, Eye, Filter, ArrowUpRight
} from 'lucide-react';

interface CreatorSuggestion {
  id: string;
  name: string;
  handle: string;
  avatar: string;
  followers: string;
  isFollowing: boolean;
}

interface AudioPopular {
  id: string;
  title: string;
  artist: string;
  duration: string;
  videoCount: string;
  cover: string;
  isPlaying?: boolean;
}

export const ExplorePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('cyberpunk aesthetic streetwear');
  const [activeCategory, setActiveCategory] = useState<'todo' | 'cuentas' | 'videos' | 'sonidos' | 'hashtags' | 'envivo'>('todo');
  const [playingAudioId, setPlayingAudioId] = useState<string | null>(null);

  // Cuentas sugeridas
  const [creators, setCreators] = useState<CreatorSuggestion[]>([
    {
      id: '1',
      name: 'Kira Vex',
      handle: '@kira_techwear',
      avatar: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=200',
      followers: '842K seguidores',
      isFollowing: false
    },
    {
      id: '2',
      name: 'NeoShibuya_Lab',
      handle: '@neo_shibuya',
      avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200',
      followers: '1.2M seguidores',
      isFollowing: false
    },
    {
      id: '3',
      name: 'AeroGhost',
      handle: '@aeroghost_fits',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200',
      followers: '490K seguidores',
      isFollowing: true
    },
    {
      id: '4',
      name: 'Cypher Couture',
      handle: '@cypher.couture',
      avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
      followers: '315K seguidores',
      isFollowing: false
    }
  ]);

  // Búsquedas recientes
  const [recentSearches, setRecentSearches] = useState<string[]>([
    'techwear jackets water repellent',
    'blade runner neon lights overlay',
    '@kira_techwear tutorials',
    'synthwave playlist workout',
    'tactical harness cargo pants'
  ]);

  // Audios populares
  const audios: AudioPopular[] = [
    {
      id: '1',
      title: 'Synthetic Pulse (Overdrive Edit)',
      artist: 'Kavinsky x Vector Seven',
      duration: '0:45',
      videoCount: '142.8K videos creados',
      cover: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=150'
    },
    {
      id: '2',
      title: 'Neo Tokyo Rain Drift (Night Versi...',
      artist: 'Subway Runner Collective',
      duration: '0:32',
      videoCount: '88.4K videos creados',
      cover: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=150'
    }
  ];

  // Videos destacados
  const featuredVideos = [
    {
      id: 1,
      title: 'Top 5 marcas underground de Cyberpunk Streetwear para...',
      author: '@cyber_k',
      authorAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50',
      views: '1.8M',
      likes: '145K',
      image: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600'
    },
    {
      id: 2,
      title: 'Cómo estilizar un chaleco táctico con piezas oversize...',
      author: '@tactical_drip',
      authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50',
      views: '890K',
      likes: '68K',
      image: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600'
    },
    {
      id: 3,
      title: 'Outfit check en Akihabara a medianoche: cyberpunk pur...',
      author: '@rei_tokyo',
      authorAvatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=50',
      views: '2.3M',
      likes: '230K',
      image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600'
    },
    {
      id: 4,
      title: 'DIY: Cómo poner luces fibra óptica en tu sudadera negra...',
      author: '@neon_mods',
      authorAvatar: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=50',
      views: '540K',
      likes: '42K',
      image: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=600'
    },
    {
      id: 5,
      title: 'Neo-Samurai: Fusión entre folclore y techwear distópic...',
      author: '@ronin_fits',
      authorAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50',
      views: '3.1M',
      likes: '398K',
      image: 'https://images.unsplash.com/photo-1552053831-71594a27632d?w=600'
    },
    {
      id: 6,
      title: 'Unboxing de los sneakers más ciberpunk del mercado:...',
      author: '@kicks_future',
      authorAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50',
      views: '970K',
      likes: '81K',
      image: 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600'
    }
  ];

  const toggleFollow = (id: string) => {
    setCreators(prev => prev.map(c => c.id === id ? { ...c, isFollowing: !c.isFollowing } : c));
  };

  const removeRecentSearch = (idx: number) => {
    setRecentSearches(prev => prev.filter((_, i) => i !== idx));
  };

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* BARRA DE BÚSQUEDA Y BOTÓN DE FILTROS */}
      <div className="flex items-center gap-3 pb-4">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
            <Search className="w-4 h-4 text-cyan-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar en Follow..."
            className="w-full bg-[#151726] border border-white/5 rounded-2xl pl-11 pr-10 py-3 text-base sm:text-sm text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50 focus:ring-1 focus:ring-pink-500/50 transition-all font-medium"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-[#171926] hover:bg-[#202334] border border-white/5 text-gray-300 hover:text-white text-xs font-semibold transition-all">
          <SlidersHorizontal className="w-4 h-4 text-pink-400" />
          <span>Filtros</span>
        </button>
      </div>

      {/* PÍLDORAS DE CATEGORÍAS */}
      <div className="flex items-center gap-2.5 overflow-x-auto pb-6 scrollbar-none text-xs font-semibold">
        <button
          onClick={() => setActiveCategory('todo')}
          className={`px-4 py-1.5 rounded-full transition-all ${
            activeCategory === 'todo'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md shadow-pink-500/20'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          Todo
        </button>

        <button
          onClick={() => setActiveCategory('cuentas')}
          className={`px-4 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
            activeCategory === 'cuentas'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>Cuentas</span>
          <span className="text-[10px] bg-white/10 px-1 rounded-full">18</span>
        </button>

        <button
          onClick={() => setActiveCategory('videos')}
          className={`px-4 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
            activeCategory === 'videos'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          <Play className="w-3.5 h-3.5" />
          <span>Videos</span>
          <span className="text-[10px] bg-white/10 px-1 rounded-full">3.4k</span>
        </button>

        <button
          onClick={() => setActiveCategory('sonidos')}
          className={`px-4 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
            activeCategory === 'sonidos'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          <Music className="w-3.5 h-3.5" />
          <span>Sonidos</span>
        </button>

        <button
          onClick={() => setActiveCategory('hashtags')}
          className={`px-4 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
            activeCategory === 'hashtags'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          <Hash className="w-3.5 h-3.5" />
          <span>Hashtags</span>
        </button>

        <button
          onClick={() => setActiveCategory('envivo')}
          className={`px-4 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
            activeCategory === 'envivo'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'bg-[#171926] text-gray-400 hover:text-white'
          }`}
        >
          <Radio className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
          <span>En Vivo</span>
        </button>
      </div>

      {/* CUERPO PRINCIPAL: 2 COLUMNAS (CONTENIDO Y LATERAL) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* COLUMNA IZQUIERDA (8 COLUMNAS): RESULTADOS Y CATÁLOGO */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* CUENTAS SUGERIDAS */}
          <div>
            <div className="flex items-center justify-between pb-4">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-pink-400" />
                <h2 className="text-sm font-bold text-white">Cuentas Sugeridas</h2>
              </div>
              <button className="text-xs text-cyan-400 hover:underline flex items-center gap-0.5">
                <span>Ver todas</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {creators.map((c) => (
                <div key={c.id} className="p-3.5 rounded-2xl bg-[#141524] border border-white/5 flex flex-col items-center text-center space-y-2 hover:border-white/10 transition-colors">
                  <div className="relative">
                    <img src={c.avatar} alt={c.name} className="w-14 h-14 rounded-full object-cover border border-purple-500/40" />
                    <span className="absolute bottom-0 right-0 w-4 h-4 rounded-full bg-cyan-500 text-white flex items-center justify-center text-[10px]">
                      <CheckCircle className="w-3 h-3 fill-black text-cyan-400" />
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block truncate w-28">{c.name}</span>
                    <span className="text-[10px] text-gray-400 block truncate w-28">{c.handle}</span>
                    <span className="text-[9px] text-gray-500 block pt-0.5">{c.followers}</span>
                  </div>
                  <button
                    onClick={() => toggleFollow(c.id)}
                    className={`w-full py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      c.isFollowing
                        ? 'bg-white/10 text-gray-300'
                        : 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-md shadow-pink-500/20 hover:brightness-110'
                    }`}
                  >
                    {c.isFollowing ? 'Siguiendo' : '+ Seguir'}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* HASHTAGS RELACIONADOS EN TENDENCIA */}
          <div>
            <div className="flex items-center gap-2 pb-3">
              <TrendingUp className="w-4 h-4 text-rose-400" />
              <h2 className="text-sm font-bold text-white">Hashtags Relacionados en Tendencia</h2>
            </div>

            <div className="flex items-center gap-2.5 flex-wrap">
              {[
                { tag: 'CyberpunkStyle', views: '43.2M vistas' },
                { tag: 'StreetwearInspo', views: '128M vistas' },
                { tag: 'NeonVibes', views: '89M vistas' },
                { tag: 'TechwearFits', views: '214.6M vistas' },
                { tag: 'DystopianFashion', views: '32.8M vistas' }
              ].map((h) => (
                <div
                  key={h.tag}
                  className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-[#141524] hover:bg-[#1a1c30] border border-white/5 cursor-pointer group transition-all"
                >
                  <div className="w-6 h-6 rounded-lg bg-pink-500/10 text-pink-400 flex items-center justify-center text-xs font-bold">
                    #
                  </div>
                  <div className="text-left">
                    <span className="text-xs font-semibold text-gray-200 group-hover:text-pink-300 block">
                      {h.tag}
                    </span>
                    <span className="text-[10px] text-gray-500">{h.views}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AUDIOS POPULARES */}
          <div>
            <div className="flex items-center justify-between pb-3">
              <div className="flex items-center gap-2">
                <Music className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm font-bold text-white">Audios Populares</h2>
              </div>
              <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider">
                TOP SONIDOS USADOS
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {audios.map((a) => (
                <div
                  key={a.id}
                  className="p-3 rounded-2xl bg-[#141524] border border-white/5 flex items-center gap-3 group hover:border-cyan-500/30 transition-colors"
                >
                  <div className="relative w-12 h-12 rounded-xl overflow-hidden flex-shrink-0">
                    <img src={a.cover} alt={a.title} className="w-full h-full object-cover" />
                    <button
                      onClick={() => setPlayingAudioId(playingAudioId === a.id ? null : a.id)}
                      className="absolute inset-0 bg-black/40 flex items-center justify-center text-white"
                    >
                      {playingAudioId === a.id ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white" />}
                    </button>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white truncate block">{a.title}</span>
                      <span className="text-[10px] text-cyan-400 font-mono">{a.duration}</span>
                    </div>
                    <span className="text-[10px] text-gray-400 block truncate">{a.artist}</span>
                    <div className="flex items-center gap-1.5 pt-1 text-[9px] text-gray-500">
                      <Radio className="w-3 h-3 text-pink-400" />
                      <span>{a.videoCount}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* VIDEOS DESTACADOS */}
          <div>
            <div className="flex items-center justify-between pb-4">
              <div className="flex items-center gap-2">
                <Play className="w-4 h-4 text-purple-400" />
                <h2 className="text-sm font-bold text-white">Videos Destacados</h2>
              </div>
              <div className="text-xs text-gray-400 flex items-center gap-1">
                <span>Ordenar por:</span>
                <span className="text-white font-semibold">Más Relevantes</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {featuredVideos.map((fv) => (
                <div
                  key={fv.id}
                  className="group relative aspect-[9/16] rounded-2xl overflow-hidden bg-[#141524] border border-white/5 hover:border-pink-500/40 cursor-pointer shadow-lg transition-all"
                >
                  <img src={fv.image} alt={fv.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-black/30 pointer-events-none"></div>

                  <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm text-[10px] text-white flex items-center gap-1">
                    <Play className="w-3 h-3 fill-white" />
                    {fv.views}
                  </div>

                  <div className="absolute bottom-3 left-3 right-3 text-white space-y-1">
                    <h3 className="text-xs font-semibold line-clamp-2 leading-tight group-hover:text-pink-300">
                      {fv.title}
                    </h3>
                    <div className="flex items-center justify-between text-[10px] text-gray-400 pt-1">
                      <div className="flex items-center gap-1">
                        <img src={fv.authorAvatar} alt="" className="w-4 h-4 rounded-full object-cover" />
                        <span className="truncate max-w-[80px]">{fv.author}</span>
                      </div>
                      <span className="flex items-center gap-1 text-rose-400">
                        <Heart className="w-3 h-3 fill-rose-400" />
                        {fv.likes}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* COLUMNA DERECHA (4 COLUMNAS): BÚSQUEDAS RECIENTES, EN VIVO Y VOLUMEN */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* BÚSQUEDAS RECIENTES */}
          <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-gray-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">Búsquedas recientes</h3>
              </div>
              {recentSearches.length > 0 && (
                <button
                  onClick={() => setRecentSearches([])}
                  className="text-[10px] font-bold text-rose-400 hover:text-rose-300 uppercase tracking-wider"
                >
                  BORRAR TODO
                </button>
              )}
            </div>

            <div className="space-y-1">
              {recentSearches.map((term, i) => (
                <div
                  key={term}
                  className="flex items-center justify-between py-2 text-xs text-gray-300 hover:text-white group border-b border-white/5 last:border-none"
                >
                  <span
                    onClick={() => setSearchQuery(term)}
                    className="cursor-pointer truncate hover:text-cyan-400 transition-colors"
                  >
                    {term}
                  </span>
                  <button
                    onClick={() => removeRecentSearch(i)}
                    className="text-gray-500 hover:text-rose-400"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
              {recentSearches.length === 0 && (
                <p className="text-xs text-gray-500 py-2">No hay búsquedas recientes.</p>
              )}
            </div>
          </div>

          {/* TRANSMISIONES EN VIVO */}
          <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">Transmisiones en Vivo</h3>
              </div>
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 bg-rose-600 text-white rounded-md tracking-wider">
                LIVE
              </span>
            </div>

            <div className="relative aspect-video rounded-2xl overflow-hidden bg-black border border-white/10 group">
              <img
                src="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600"
                alt="Tokyo Techwear Week 2025"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40"></div>

              <div className="absolute top-2.5 left-2.5 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-md text-[10px] text-white flex items-center gap-1.5">
                <Eye className="w-3 h-3 text-rose-400" />
                <span>12.6K viendo</span>
              </div>

              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-white leading-tight">Tokyo Techwear Week 2025</h4>
                  <span className="text-[10px] text-gray-400">@tokyofashion_tv</span>
                </div>
                <button className="px-3 py-1 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold transition-all shadow-md shadow-cyan-500/20">
                  Unirse
                </button>
              </div>
            </div>
          </div>

          {/* VOLUMEN DE BÚSQUEDA (GRÁFICA SPLINE) */}
          <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400 font-medium">Volumen de Búsqueda</span>
              <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full">
                +48% esta semana
              </span>
            </div>

            <div>
              <span className="text-2xl font-black text-white">4.2M</span>
              <span className="text-xs text-gray-400 ml-2">Interacciones totales</span>
            </div>

            {/* SVG Curva Spline con gradiente cian */}
            <div className="h-20 w-full pt-2">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 200 60" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="cyanLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="50%" stopColor="#ec4899" />
                    <stop offset="100%" stopColor="#00f2fe" />
                  </linearGradient>
                </defs>
                <path
                  d="M 0 50 Q 50 48, 80 40 T 150 25 T 200 10"
                  fill="none"
                  stroke="url(#cyanLineGrad)"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
                <circle cx="200" cy="10" r="4" fill="#00f2fe" className="animate-pulse" />
              </svg>
            </div>

            <p className="text-[11px] text-gray-400 leading-relaxed pt-1">
              El interés por moda ciberpunk urbana alcanzó su punto máximo impulsado por festivales de synthwave y nuevas colecciones técnicas.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
};
