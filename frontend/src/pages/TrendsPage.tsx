/**
 * Pantalla de Tendencias (Follow Trends).
 * Catalogo de videos virales en ranking, sonidos en ascenso y hashtags con metricas en vivo.
 */

import React, { useState } from 'react';
import { 
  Flame, TrendingUp, Music, Hash, Play, Heart, 
  Share2, Eye, Radio, Sparkles, Filter, ChevronRight
} from 'lucide-react';

interface TrendingVideo {
  rank: number;
  title: string;
  creator: string;
  creatorAvatar: string;
  views: string;
  likes: string;
  image: string;
  tag: string;
  change: string;
}

export const TrendsPage: React.FC = () => {
  const [filterPeriod, setFilterPeriod] = useState<'hoy' | 'semana' | 'mes'>('hoy');
  const [activeCategory, setActiveCategory] = useState<'general' | 'musica' | 'tecnologia' | 'gaming' | 'moda'>('general');

  const rankingVideos: TrendingVideo[] = [
    {
      rank: 1,
      title: "Outfit check en Akihabara a medianoche: cyberpunk puro y luces reactivas",
      creator: "@rei_tokyo",
      creatorAvatar: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100",
      views: "4.8M",
      likes: "620K",
      image: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
      tag: "#CyberpunkStyle",
      change: "+124% viral"
    },
    {
      rank: 2,
      title: "Configurando el nuevo setup holografico para streaming nocturno",
      creator: "@valeria_creatrix",
      creatorAvatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100",
      views: "3.4M",
      likes: "1.2M",
      image: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600",
      tag: "#techtrends",
      change: "+89% viral"
    },
    {
      rank: 3,
      title: "Neo-Samurai: Fusion entre folclore y techwear distopico en Shibuya",
      creator: "@cypher.couture",
      creatorAvatar: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100",
      views: "3.1M",
      likes: "398K",
      image: "https://images.unsplash.com/photo-1552053831-71594a27632d?w=600",
      tag: "#DystopianFashion",
      change: "+64% viral"
    },
    {
      rank: 4,
      title: "Top 5 marcas underground de Cyberpunk Streetwear para 2026",
      creator: "@kira_techwear",
      creatorAvatar: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=100",
      views: "2.4M",
      likes: "210K",
      image: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600",
      tag: "#StreetwearInspo",
      change: "+52% viral"
    },
    {
      rank: 5,
      title: "ASMR Custom Keyboard Build con switches lubricados a mano",
      creator: "@valeria_creatrix",
      creatorAvatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100",
      views: "1.9M",
      likes: "185K",
      image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
      tag: "#setup",
      change: "+41% viral"
    },
    {
      rank: 6,
      title: "Unboxing de los sneakers mas ciberpunk del mercado: edicion limitada",
      creator: "@kicks_future",
      creatorAvatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100",
      views: "1.5M",
      likes: "128K",
      image: "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600",
      tag: "#StreetwearInspo",
      change: "+38% viral"
    }
  ];

  const viralHashtags = [
    { tag: "CyberpunkStyle", volume: "43.2M", growth: "+48%", status: "En alza" },
    { tag: "TechwearFits", volume: "214.6M", growth: "+36%", status: "Top 1" },
    { tag: "StreetwearInspo", volume: "128.0M", growth: "+29%", status: "Estable" },
    { tag: "NeonVibes", volume: "89.4M", growth: "+54%", status: "En alza" },
    { tag: "DystopianFashion", volume: "32.8M", growth: "+18%", status: "Nuevo" },
    { tag: "CustomKeyboards", volume: "18.2M", growth: "+62%", status: "En alza" }
  ];

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      
      {/* CABECERA DE TENDENCIAS */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-500 to-amber-500 flex items-center justify-center shadow-lg shadow-rose-500/20">
              <Flame className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white font-sans">
              Tendencias Globales
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-rose-500/20 border border-rose-500/30 text-rose-300 text-[10px] font-bold tracking-wider">
              EN TIEMPO REAL
            </span>
          </div>
          <p className="text-xs text-gray-400">
            Descubre los creadores, sonidos y esteticas con mayor aceleracion algoritmica en las ultimas 24 horas.
          </p>
        </div>

        {/* Filtros de periodo */}
        <div className="flex items-center gap-1 bg-[#141524] p-1 rounded-2xl border border-white/5 text-xs font-semibold self-start sm:self-auto">
          {(['hoy', 'semana', 'mes'] as const).map((period) => (
            <button
              key={period}
              onClick={() => setFilterPeriod(period)}
              className={`px-3.5 py-1.5 rounded-xl capitalize transition-all ${
                filterPeriod === period
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {period === 'hoy' ? 'Hoy' : period === 'semana' ? 'Esta Semana' : 'Este Mes'}
            </button>
          ))}
        </div>
      </div>

      {/* CHIPS DE CATEGORIAS */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none text-xs font-semibold">
        {(['general', 'musica', 'tecnologia', 'gaming', 'moda'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-1.5 rounded-full capitalize transition-all ${
              activeCategory === cat
                ? 'bg-white/15 text-white border border-white/20'
                : 'bg-[#151624] text-gray-400 hover:text-white border border-white/5'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* CUERPO: 2 COLUMNAS (RANKING PRINCIPAL Y RADAR DE HASHTAGS/SONIDOS) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* COLUMNA IZQUIERDA (8 COLUMNAS): RANKING DE VIDEOS VIRALES */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between pb-1">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Top Videos Virales</h2>
            </div>
            <span className="text-[11px] text-gray-400">Actualizado cada 5 minutos</span>
          </div>

          <div className="space-y-3">
            {rankingVideos.map((video) => (
              <div
                key={video.rank}
                className="group p-3.5 rounded-2xl bg-[#141524] border border-white/5 hover:border-pink-500/30 transition-all flex items-center gap-4 cursor-pointer"
              >
                {/* Posicion del Ranking */}
                <div className="w-8 text-center flex-shrink-0">
                  <span className={`text-xl font-black font-mono ${
                    video.rank === 1 ? 'text-amber-400' : video.rank === 2 ? 'text-gray-300' : video.rank === 3 ? 'text-amber-600' : 'text-gray-500'
                  }`}>
                    #{video.rank}
                  </span>
                </div>

                {/* Miniatura */}
                <div className="relative w-20 sm:w-24 aspect-[9/14] rounded-xl overflow-hidden flex-shrink-0 bg-black">
                  <img src={video.image} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                  <span className="absolute bottom-1 right-1 text-[9px] font-bold text-white bg-black/60 px-1 rounded flex items-center gap-0.5">
                    <Play className="w-2.5 h-2.5 fill-white" />
                    {video.views}
                  </span>
                </div>

                {/* Descripcion y Datos */}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-pink-400 font-mono">{video.tag}</span>
                    <span className="text-[10px] text-emerald-400 font-semibold bg-emerald-500/10 px-1.5 py-0.2 rounded">
                      {video.change}
                    </span>
                  </div>
                  <h3 className="text-xs sm:text-sm font-bold text-white line-clamp-2 leading-snug group-hover:text-pink-300 transition-colors">
                    {video.title}
                  </h3>
                  <div className="flex items-center gap-2 pt-1 text-xs text-gray-400">
                    <img src={video.creatorAvatar} alt="" className="w-5 h-5 rounded-full object-cover border border-white/10" />
                    <span className="text-gray-300 font-semibold text-xs truncate">{video.creator}</span>
                    <span className="text-gray-600">•</span>
                    <span className="flex items-center gap-1 text-rose-400 text-xs">
                      <Heart className="w-3.5 h-3.5 fill-rose-400" />
                      {video.likes}
                    </span>
                  </div>
                </div>

                {/* Accion rapida */}
                <button className="hidden sm:flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white text-xs font-semibold border border-white/5 transition-colors">
                  <Play className="w-3 h-3 fill-white" />
                  <span>Ver</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* COLUMNA DERECHA (4 COLUMNAS): HASHTAGS EN ALZA Y RADAR VIRAL */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* HASHTAGS CON MAYOR CRECIMIENTO */}
          <div className="p-5 rounded-3xl bg-[#141524] border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-pink-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">Hashtags en Alza</h3>
              </div>
              <span className="text-[10px] text-gray-500 font-mono">24 HORAS</span>
            </div>

            <div className="space-y-2.5">
              {viralHashtags.map((h, i) => (
                <div key={h.tag} className="flex items-center justify-between p-2 rounded-xl hover:bg-white/5 transition-colors">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-mono font-bold text-gray-500">0{i + 1}</span>
                    <div>
                      <span className="text-xs font-bold text-white block">#{h.tag}</span>
                      <span className="text-[10px] text-gray-400">{h.volume} reproducciones</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-cyan-400 font-mono block">{h.growth}</span>
                    <span className="text-[9px] text-gray-500 uppercase">{h.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* TARJETA RADAR DE AUDIOS VIRALES */}
          <div className="p-5 rounded-3xl bg-gradient-to-br from-[#1a1c30] to-[#12131f] border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400">
                <Radio className="w-4 h-4 animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider">Radar de Sonidos</span>
              </div>
              <span className="text-[10px] font-mono text-pink-400 bg-pink-500/10 px-2 py-0.5 rounded-full">
                Top 3 en EspaÃ±a
              </span>
            </div>

            <p className="text-xs text-gray-300 leading-relaxed">
              Los tracks con mayor tasa de remixes creados en las ultimas 6 horas:
            </p>

            <div className="space-y-2 pt-1">
              {[
                { title: "Synthetic Pulse (Overdrive Edit)", artist: "Kavinsky x Vector Seven", uses: "+48K hoy" },
                { title: "Neo Tokyo Rain Drift (Night Version)", artist: "Subway Runner Collective", uses: "+32K hoy" },
                { title: "Original Sound - Valeria Studio", artist: "Valeria Gomez", uses: "+19K hoy" }
              ].map((song) => (
                <div key={song.title} className="p-2.5 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
                  <div className="overflow-hidden pr-2">
                    <span className="text-xs font-bold text-white block truncate">{song.title}</span>
                    <span className="text-[10px] text-gray-400 block truncate">{song.artist}</span>
                  </div>
                  <span className="text-[10px] font-mono text-rose-400 font-semibold flex-shrink-0">
                    {song.uses}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
