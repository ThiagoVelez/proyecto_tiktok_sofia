/**
 * Pantalla 5: Estudio de Publicacion y Edicion Avanzada (Creator Studio V2.4).
 * Incluye seccion dedicada para Metricas Privadas del Creador con la tarjeta
 * "ALCANCE EN TIEMPO REAL (+28.4%)" impulsada por IA, trimmer interactivo y mezclador de audio.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, Pause, Maximize2, Radio, Music, Wand2, Type, 
  Smile, Gauge, Scissors, Cloud, Upload, Globe, 
  Users, Lock, X, Check, ArrowRight, Sparkles, MessageSquare, 
  Share2, Download, Film, Sliders, Volume2, SlidersHorizontal, 
  TrendingUp, BarChart3, Eye, Zap, ShieldAlert, ArrowUpRight
} from 'lucide-react';
import { publishVideo } from '../services/api';

export const StudioPage: React.FC = () => {
  const navigate = useNavigate();
  const [studioMode, setStudioMode] = useState<'editor' | 'analytics'>('editor');

  // Estados del Formulario
  const [title, setTitle] = useState('Mi nuevo setup nocturno 2025 ✨');
  const [description, setDescription] = useState(
    'Arme por fin el espacio de trabajo definitivo para diseno, codigo y streaming de madrugada. Todos los perifericos sincronizados con el ecosistema Follow y paleta cyberpunk. Dejame en comentarios que gadget te gusto mas.'
  );
  const [selectedFilter, setSelectedFilter] = useState('Neo Glow');
  const [tags, setTags] = useState<string[]>(['follow', 'tech', 'setup', 'creator', 'viral', 'aesthetic']);
  const [collaborators, setCollaborators] = useState<string[]>(['@alex_neon', '@cyberluna']);
  const [newCollabInput, setNewCollabInput] = useState('');
  const [selectedThumbnail, setSelectedThumbnail] = useState<number>(0);
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>('public');
  const [allowComments, setAllowComments] = useState(true);
  const [allowDuet, setAllowDuet] = useState(true);
  const [allowDownloads, setAllowDownloads] = useState(false);

  // Estados de Edicion de Video y Puntos de Corte
  const [startCut, setStartCut] = useState(3.20);
  const [endCut, setEndCut] = useState(35.80);
  const [clipVolume, setClipVolume] = useState(100);
  const [musicVolume, setMusicVolume] = useState(75);
  const [showMixerModal, setShowMixerModal] = useState(false);
  const [audioPreset, setAudioPreset] = useState<'equilibrado' | 'voz' | 'graves'>('equilibrado');

  // Estados de Reproduccion y Publicacion
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState('');

  const durationCut = Math.max(0, endCut - startCut).toFixed(1);

  const thumbnails = [
    'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300',
    'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=300'
  ];

  const handleAddTag = (t: string) => {
    if (!tags.includes(t)) {
      setTags([...tags, t]);
      setDescription((prev) => `${prev} #${t}`);
    }
  };

  const handleRemoveCollaborator = (c: string) => {
    setCollaborators(collaborators.filter(item => item !== c));
  };

  const handleAddCollaborator = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && newCollabInput.trim()) {
      e.preventDefault();
      const formatted = newCollabInput.startsWith('@') ? newCollabInput.trim() : `@${newCollabInput.trim()}`;
      if (!collaborators.includes(formatted)) {
        setCollaborators([...collaborators, formatted]);
      }
      setNewCollabInput('');
    }
  };

  const handleApplyAudioPreset = (preset: 'equilibrado' | 'voz' | 'graves') => {
    setAudioPreset(preset);
    if (preset === 'voz') {
      setClipVolume(130);
      setMusicVolume(40);
    } else if (preset === 'graves') {
      setClipVolume(90);
      setMusicVolume(95);
    } else {
      setClipVolume(100);
      setMusicVolume(75);
    }
  };

  const handlePublish = async () => {
    setIsPublishing(true);
    setFeedbackMsg('');
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('visibility', visibility);
      formData.append('allow_comments', String(allowComments));
      formData.append('allow_duet', String(allowDuet));

      const res = await publishVideo(formData);
      if (res.success) {
        setFeedbackMsg('Publicacion exitosa en Follow. Redirigiendo al perfil...');
        setTimeout(() => navigate('/perfil'), 1500);
      }
    } catch (err: unknown) {
      const error = err as Error;
      setFeedbackMsg(`Error: ${error.message}`);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-10 max-w-7xl mx-auto space-y-6">
      
      {/* CABECERA: TITULO DEL ESTUDIO, CONMUTADOR DE VISTA Y AUTOGUARDADO */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/5">
        <div>
          <span className="text-[10px] font-mono font-bold tracking-wider text-pink-400 uppercase block">
            • CREATOR STUDIO V2.4 • EDICION AVANZADA
          </span>
          <div className="flex items-center gap-3 pt-0.5">
            <h1 className="text-2xl font-black tracking-tight text-white font-sans">
              Estudio de Publicacion
            </h1>
            <span className="px-2.5 py-0.5 rounded-md bg-purple-900/50 text-purple-300 border border-purple-500/30 text-[10px] font-bold tracking-wider">
              4K HDR READY
            </span>
          </div>
        </div>

        {/* Conmutador de modo: Editor vs Metricas Privadas */}
        <div className="flex items-center gap-2">
          <div className="flex items-center p-1 bg-[#141524] rounded-2xl border border-white/5 text-xs font-semibold">
            <button
              onClick={() => setStudioMode('editor')}
              className={`px-3.5 py-1.5 rounded-xl transition-all ${
                studioMode === 'editor'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Editor de Video
            </button>
            <button
              onClick={() => setStudioMode('analytics')}
              className={`px-3.5 py-1.5 rounded-xl transition-all flex items-center gap-1.5 ${
                studioMode === 'analytics'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Metricas Privadas</span>
            </button>
          </div>

          <div className="hidden md:flex items-center gap-2 text-xs text-gray-400 bg-[#141524] px-3.5 py-2 rounded-2xl border border-white/5">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Borrador autoguardado a las 02:41 AM</span>
          </div>
        </div>
      </div>

      {feedbackMsg && (
        <div className="p-3.5 rounded-2xl bg-gradient-to-r from-purple-900/70 to-pink-900/70 border border-pink-500/40 text-xs font-semibold text-white shadow-lg">
          {feedbackMsg}
        </div>
      )}

      {/* VISTA 1: METRICAS PRIVADAS DEL CREADOR (Incorporando la tarjeta exacta de Alcance en tiempo real) */}
      {studioMode === 'analytics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            
            {/* TARJETA EXACTA REPLICADA DE (ALCANCE EN TIEMPO REAL +28.4%) */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/10 space-y-4 shadow-xl relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
                  ALCANCE EN TIEMPO REAL
                </span>
                <span className="text-rose-400 font-extrabold text-sm font-mono bg-rose-500/10 px-2.5 py-0.5 rounded-full">
                  +28.4%
                </span>
              </div>

              {/* Grafica Spline curva suave con degradado magenta */}
              <div className="h-28 w-full pt-2 flex items-center justify-center">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 200 60" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="pinkReachGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#ec4899" />
                      <stop offset="100%" stopColor="#ff2a85" />
                    </linearGradient>
                  </defs>
                  <path
                    d="M 10 50 Q 70 47, 110 38 T 160 25 T 195 12"
                    fill="none"
                    stroke="url(#pinkReachGrad)"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                  />
                  <circle cx="195" cy="12" r="4.5" fill="#ff2a85" className="animate-pulse" />
                </svg>
              </div>

              <div className="pt-1 border-t border-white/5">
                <span className="text-xs text-gray-400 block font-medium">
                  Feed en directo impulsado por IA
                </span>
              </div>
            </div>

            {/* Metrica 2: Retencion Media de Audiencia */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/10 space-y-3 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
                  RETENCION MEDIA
                </span>
                <span className="text-cyan-400 font-extrabold text-xs font-mono bg-cyan-500/10 px-2.5 py-0.5 rounded-full">
                  +12.8%
                </span>
              </div>

              <div>
                <span className="text-3xl font-black text-white font-mono">74.2%</span>
                <span className="text-xs text-gray-400 block mt-1">Tiempo de visualizacion completada</span>
              </div>

              <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden mt-4">
                <div className="w-3/4 h-full bg-cyan-400 rounded-full"></div>
              </div>
            </div>

            {/* Metrica 3: Distribucion Algoritmica de Trafico */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/10 space-y-3 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
                  ORIGEN DE VISITAS
                </span>
                <span className="text-purple-400 font-bold text-xs">Feed Para Ti</span>
              </div>

              <div className="space-y-2 text-xs pt-1">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Feed Para Ti (Algoritmo)</span>
                  <span className="font-mono font-bold text-white">82%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Perfil Directo & Shorts</span>
                  <span className="font-mono font-bold text-white">12%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Catalogo de Sonidos</span>
                  <span className="font-mono font-bold text-white">6%</span>
                </div>
              </div>
            </div>

          </div>

          <div className="p-4 rounded-2xl bg-[#18192a] border border-white/10 flex items-center justify-between text-xs">
            <span className="text-gray-300">
              Estas metricas son estrictamente privadas y solo visibles para la cuenta de Valeria Gomez en este dispositivo.
            </span>
            <button
              onClick={() => setStudioMode('editor')}
              className="px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-bold transition-colors"
            >
              Volver al Editor de Publicacion
            </button>
          </div>
        </div>
      )}

      {/* VISTA 2: EDITOR DE VIDEO Y PUBLICACION */}
      {studioMode === 'editor' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* COLUMNA IZQUIERDA (5 COLUMNAS): PREVIEW DEL VIDEO Y CONTROLES DE EDICION */}
          <div className="lg:col-span-5 space-y-5">
            
            {/* Smart Container de Video Vertical */}
            <div className="relative aspect-[9/16] w-full max-w-[380px] mx-auto rounded-[32px] overflow-hidden bg-black border border-white/10 shadow-2xl flex flex-col justify-between p-4">
              
              <img
                src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800"
                alt="Setup de trabajo"
                className={`absolute inset-0 w-full h-full object-cover transition-all ${
                  selectedFilter === 'Neo Glow' ? 'contrast-125 saturate-125' :
                  selectedFilter === 'Cyber Cyan' ? 'hue-rotate-30 saturate-150' :
                  selectedFilter === 'Vintage 90s' ? 'sepia-50 contrast-110' : ''
                }`}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80 pointer-events-none"></div>

              {/* Cabecera interna: REC timer y Expand */}
              <div className="relative z-10 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-mono border border-white/10">
                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                  <span>REC • 00:32 / 00:45</span>
                </div>

                <div className="flex items-center gap-1.5">
                  <button className="p-1.5 rounded-full bg-black/60 backdrop-blur-md text-white hover:bg-black/80">
                    <Maximize2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Pildora de Audio insertado */}
              <div className="relative z-10 self-center bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center gap-2 text-xs text-cyan-300">
                <Music className="w-3.5 h-3.5 text-pink-400" />
                <span className="truncate max-w-[200px] text-[11px]">Midnight Synthwave • Neon Drift (Original M...</span>
              </div>

              {/* Boton Central Play/Pause */}
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="absolute inset-0 m-auto w-14 h-14 rounded-full bg-white/20 backdrop-blur-md border border-white/30 flex items-center justify-center text-white hover:scale-110 active:scale-95 transition-all shadow-xl"
              >
                {isPlaying ? <Pause className="w-6 h-6 fill-white" /> : <Play className="w-6 h-6 fill-white ml-1" />}
              </button>

              {/* Paleta vertical de herramientas a la derecha del video */}
              <div className="absolute right-3 top-24 z-10 flex flex-col items-center gap-3 bg-black/50 backdrop-blur-md p-1.5 rounded-2xl border border-white/10 text-white">
                <button onClick={() => setShowMixerModal(true)} className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Music className="w-4 h-4 text-cyan-400" />
                  <span className="text-[8px] font-bold">Audio</span>
                </button>
                <button className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Wand2 className="w-4 h-4 text-pink-400" />
                  <span className="text-[8px] font-bold">Filtros</span>
                </button>
                <button className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Type className="w-4 h-4 text-purple-400" />
                  <span className="text-[8px] font-bold">Texto</span>
                </button>
                <button className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Smile className="w-4 h-4 text-amber-400" />
                  <span className="text-[8px] font-bold">Stickers</span>
                </button>
                <button className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Gauge className="w-4 h-4 text-emerald-400" />
                  <span className="text-[8px] font-bold">1.0x</span>
                </button>
                <button className="p-2 rounded-xl hover:bg-white/10 flex flex-col items-center gap-0.5">
                  <Scissors className="w-4 h-4 text-rose-400" />
                  <span className="text-[8px] font-bold">Split</span>
                </button>
              </div>

              {/* Texto de subtitulo overlay */}
              <div className="relative z-10 text-center pb-2">
                <span className="px-3 py-1 rounded-xl bg-black/70 backdrop-blur-md text-white text-xs font-semibold border border-white/10 shadow-lg">
                  "Este es el mejor angulo para programar..."
                </span>
              </div>

            </div>

            {/* Filtros Rapidos */}
            <div className="space-y-2">
              <span className="text-xs text-gray-400 font-medium">Filtros rapidos aplicados:</span>
              <div className="flex items-center gap-2 flex-wrap text-xs">
                {['Neo Glow', 'Cyber Cyan', 'Vintage 90s', '4K Crisp Enhance'].map((filterName) => (
                  <button
                    key={filterName}
                    onClick={() => setSelectedFilter(filterName)}
                    className={`px-3 py-1.5 rounded-full font-semibold transition-all ${
                      selectedFilter === filterName
                        ? 'bg-pink-600 text-white shadow-md shadow-pink-500/25'
                        : 'bg-[#151624] text-gray-300 hover:text-white border border-white/5'
                    }`}
                  >
                    {selectedFilter === filterName && '• '}
                    {filterName}
                  </button>
                ))}
              </div>
            </div>

            {/* LINEA DE TIEMPO / SCRUBBER DE CORTE INTERACTIVO */}
            <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-3 shadow-inner">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-300 font-mono">
                  Puntos de corte: [00:0{startCut.toFixed(2)} - 00:{endCut.toFixed(2)}]
                </span>
                <span className="text-pink-400 font-mono font-bold">
                  Duracion: {durationCut}s
                </span>
              </div>

              {/* Pista de corte con sliders visuales interactivos */}
              <div className="relative h-12 rounded-xl bg-[#0e0f19] border border-white/10 flex flex-col justify-center px-4 overflow-hidden">
                <div
                  className="absolute h-full bg-pink-500/25 border-y border-pink-500/50"
                  style={{
                    left: `${(startCut / 45) * 100}%`,
                    right: `${100 - (endCut / 45) * 100}%`
                  }}
                ></div>

                <div className="w-full flex items-center justify-between opacity-40 text-[9px] font-mono pointer-events-none select-none">
                  <span>00:00</span>
                  <span>00:15</span>
                  <span>00:30</span>
                  <span>00:45</span>
                </div>

                <div className="absolute inset-x-2 flex items-center justify-between pointer-events-auto">
                  <input
                    type="range"
                    min="0"
                    max="40"
                    step="0.1"
                    value={startCut}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      if (val < endCut - 2) setStartCut(val);
                    }}
                    className="w-1/2 accent-pink-500 cursor-pointer opacity-80 hover:opacity-100"
                  />
                  <input
                    type="range"
                    min="5"
                    max="45"
                    step="0.1"
                    value={endCut}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      if (val > startCut + 2) setEndCut(val);
                    }}
                    className="w-1/2 accent-pink-500 cursor-pointer opacity-80 hover:opacity-100"
                  />
                </div>
              </div>

              {/* Balances de Audio y Boton Mezclador */}
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-300 pt-1">
                <span className="font-mono text-gray-400">Volumen clip: {clipVolume}%</span>
                <span className="font-mono text-gray-400">Musica: {musicVolume}%</span>
                <button
                  onClick={() => setShowMixerModal(true)}
                  className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>Mezclador de audio</span>
                </button>
              </div>
            </div>

            {/* WIDGET DE ALCANCE EN TIEMPO REAL INSERTADO EN EL ESTUDIO */}
            <div className="p-4 rounded-3xl bg-[#141524] border border-white/5 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 font-medium font-mono text-[11px]">ALCANCE EN TIEMPO REAL</span>
                <span className="text-rose-400 font-bold font-mono text-[11px]">+28.4%</span>
              </div>

              <div className="h-16 w-full pt-1">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 160 40">
                  <path
                    d="M 0 35 Q 40 33, 70 28 T 120 18 T 160 8"
                    fill="none"
                    stroke="#ec4899"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                </svg>
              </div>

              <p className="text-[10px] text-gray-500">
                Feed en directo impulsado por IA
              </p>
            </div>

          </div>

          {/* COLUMNA DERECHA (7 COLUMNAS): DETALLES, METADATOS Y PUBLICACION */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* TARJETA 1: DETALLES DEL CONTENIDO */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/5 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Film className="w-4 h-4 text-cyan-400" />
                  <span>Detalles del Contenido</span>
                </h2>
                <span className="text-[10px] font-mono text-gray-400 bg-white/5 px-2.5 py-0.5 rounded-full">
                  Paso 2 de 2
                </span>
              </div>

              {/* Titulo del video */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <label className="text-gray-300 font-semibold">Titulo del video</label>
                  <span className="text-[10px] text-gray-500 font-mono">{title.length} / 100</span>
                </div>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  maxLength={100}
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-2xl px-4 py-3 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50"
                />
              </div>

              {/* Descripcion detallada */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <label className="text-gray-300 font-semibold">Descripcion detallada</label>
                  <span className="text-[10px] text-gray-500 font-mono">{description.length} / 2200</span>
                </div>
                <textarea
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={2200}
                  className="w-full bg-[#1b1c2e] border border-white/10 rounded-2xl p-4 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50 leading-relaxed resize-none"
                />
              </div>

              {/* Hashtags sugeridos */}
              <div className="space-y-2">
                <label className="text-xs text-gray-400 font-medium block">
                  # Hashtags inteligentes sugeridos (clic para insertar)
                </label>
                <div className="flex items-center gap-2 flex-wrap text-xs">
                  {['follow', 'tech', 'setup', 'creator', 'viral', 'aesthetic'].map((tag) => (
                    <button
                      key={tag}
                      onClick={() => handleAddTag(tag)}
                      className="px-3 py-1 rounded-xl bg-[#1b1c2e] hover:bg-pink-600/30 text-gray-300 hover:text-pink-300 border border-white/5 transition-colors font-mono text-[11px]"
                    >
                      #{tag}
                    </button>
                  ))}
                  <button className="px-3 py-1 rounded-xl border border-dashed border-gray-600 text-gray-400 hover:text-white text-[11px]">
                    + Nuevo tag
                  </button>
                </div>
              </div>

              {/* Colaboradores / Menciones */}
              <div className="space-y-2">
                <label className="text-xs text-gray-400 font-medium block">
                  Mencionar Creadores • Colaboradores
                </label>
                <div className="flex items-center gap-2 flex-wrap">
                  {collaborators.map((c) => (
                    <span
                      key={c}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-purple-900/40 text-purple-200 border border-purple-500/30 text-xs font-semibold"
                    >
                      <span>{c}</span>
                      <button onClick={() => handleRemoveCollaborator(c)} className="hover:text-rose-400">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                  <input
                    type="text"
                    value={newCollabInput}
                    onChange={(e) => setNewCollabInput(e.target.value)}
                    onKeyDown={handleAddCollaborator}
                    placeholder="Escribe @usuario para invitar..."
                    className="flex-1 min-w-[200px] bg-transparent text-xs text-white placeholder-gray-500 focus:outline-none py-1"
                  />
                </div>
              </div>

            </div>

            {/* TARJETA 2: PORTADA & MINIATURA */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">Portada & Miniatura</h3>
                  <p className="text-[11px] text-gray-400">
                    Selecciona el fotograma clave que cautivara en el feed de Explorar
                  </p>
                </div>
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1b1c2e] hover:bg-white/10 text-xs font-semibold text-gray-200 border border-white/5 transition-colors">
                  <Upload className="w-3.5 h-3.5 text-pink-400" />
                  <span>Subir propia</span>
                </button>
              </div>

              <div className="grid grid-cols-4 gap-3">
                {thumbnails.map((thumbUrl, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedThumbnail(idx)}
                    className={`relative aspect-[9/16] rounded-2xl overflow-hidden cursor-pointer border-2 transition-all ${
                      selectedThumbnail === idx
                        ? 'border-pink-500 shadow-lg shadow-pink-500/20'
                        : 'border-white/5 opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={thumbUrl} alt="" className="w-full h-full object-cover" />
                    {selectedThumbnail === idx && (
                      <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-pink-600 text-[9px] font-bold uppercase tracking-wider text-white">
                        Activa
                      </span>
                    )}
                    {idx === 2 && (
                      <span className="absolute bottom-1.5 right-1.5 px-1 py-0.5 rounded bg-black/70 text-[8px] font-mono text-gray-300">
                        00:22
                      </span>
                    )}
                  </div>
                ))}

                <div className="aspect-[9/16] rounded-2xl border border-dashed border-gray-600 flex flex-col items-center justify-center p-2 text-center text-gray-400 hover:border-pink-500 cursor-pointer transition-colors">
                  <Scissors className="w-5 h-5 text-gray-500 mb-1" />
                  <span className="text-[9px] font-medium leading-tight">Elegir otro fotograma</span>
                </div>
              </div>
            </div>

            {/* TARJETA 3: PRIVACIDAD Y OPCIONES DE AUDIENCIA */}
            <div className="p-6 rounded-3xl bg-[#141524] border border-white/5 space-y-5">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                PRIVACIDAD Y OPCIONES DE AUDIENCIA
              </h3>

              {/* Selector Segmentado de Audiencia */}
              <div className="space-y-2">
                <span className="text-xs text-gray-300 font-semibold block">Quien puede ver este video</span>
                <p className="text-[11px] text-gray-500 -mt-1">
                  Controla la distribucion en feeds globales y algoritmos
                </p>
                <div className="grid grid-cols-3 p-1 bg-[#1b1c2e] rounded-2xl border border-white/5 text-xs font-semibold">
                  <button
                    type="button"
                    onClick={() => setVisibility('public')}
                    className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
                      visibility === 'public' ? 'bg-[#292c45] text-white shadow' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Globe className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Publico</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setVisibility('friends')}
                    className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
                      visibility === 'friends' ? 'bg-[#292c45] text-white shadow' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Users className="w-3.5 h-3.5 text-pink-400" />
                    <span>Amigos</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setVisibility('private')}
                    className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
                      visibility === 'private' ? 'bg-[#292c45] text-white shadow' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Lock className="w-3.5 h-3.5 text-gray-400" />
                    <span>Solo yo</span>
                  </button>
                </div>
              </div>

              {/* Switches de interaccion */}
              <div className="space-y-4 pt-2">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-white block">Permitir comentarios</span>
                    <span className="text-[11px] text-gray-400">Tus seguidores podran debatir en tu publicacion</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setAllowComments(!allowComments)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                      allowComments ? 'bg-purple-600' : 'bg-gray-700'
                    }`}
                  >
                    <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                      allowComments ? 'translate-x-5' : 'translate-x-0'
                    }`}></div>
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-white block">Permitir Duos y Remix (Pegar)</span>
                    <span className="text-[11px] text-gray-400">Impulsa tu alcance permitiendo reacciones a tu clip</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setAllowDuet(!allowDuet)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                      allowDuet ? 'bg-purple-600' : 'bg-gray-700'
                    }`}
                  >
                    <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                      allowDuet ? 'translate-x-5' : 'translate-x-0'
                    }`}></div>
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-white block">Permitir descargas del video</span>
                    <span className="text-[11px] text-gray-400">Los espectadores podran guardar el video con marca de agua</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setAllowDownloads(!allowDownloads)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                      allowDownloads ? 'bg-purple-600' : 'bg-gray-700'
                    }`}
                  >
                    <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                      allowDownloads ? 'translate-x-5' : 'translate-x-0'
                    }`}></div>
                  </button>
                </div>
              </div>

            </div>

            {/* BARRA INFERIOR DE ACCIONES */}
            <div className="flex items-center justify-end gap-3 pt-4">
              <button
                onClick={() => navigate('/')}
                className="px-6 py-3 rounded-2xl bg-[#1b1c2e] hover:bg-[#252740] text-gray-300 text-xs font-bold transition-all"
              >
                Cancelar
              </button>

              <button
                onClick={() => setFeedbackMsg('Borrador guardado exitosamente.')}
                className="px-6 py-3 rounded-2xl bg-[#1b1c2e] hover:bg-[#252740] text-gray-300 text-xs font-bold transition-all"
              >
                Guardar en borrador
              </button>

              <button
                onClick={handlePublish}
                disabled={isPublishing}
                className="px-8 py-3 rounded-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-rose-400 text-white text-xs font-bold shadow-xl shadow-pink-500/25 hover:brightness-110 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isPublishing ? 'Publicando...' : 'Publicar Video'}</span>
              </button>
            </div>

          </div>

        </div>
      )}

      {/* MODAL MEZCLADOR DE AUDIO */}
      {showMixerModal && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setShowMixerModal(false)}
        >
          <div
            className="relative w-full max-w-md rounded-3xl bg-[#141524] border border-white/10 shadow-2xl p-6 space-y-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2 text-cyan-400">
                <Sliders className="w-4 h-4" />
                <h3 className="text-sm font-bold text-white">Mezclador de Audio Profesional</h3>
              </div>
              <button onClick={() => setShowMixerModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2">
              <span className="text-xs text-gray-400 font-medium">Perfiles de Sonido Rapidos:</span>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { key: 'equilibrado', label: 'Equilibrado' },
                  { key: 'voz', label: 'Voz Inteligente' },
                  { key: 'graves', label: 'Graves Synth' }
                ].map((p) => (
                  <button
                    key={p.key}
                    type="button"
                    onClick={() => handleApplyAudioPreset(p.key as any)}
                    className={`py-2 rounded-xl text-xs font-semibold border transition-all ${
                      audioPreset === p.key
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-sm'
                        : 'bg-[#1b1c2e] text-gray-400 border-white/5 hover:text-white'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-300 font-medium">Volumen del Clip Original</span>
                  <span className="text-cyan-400 font-mono font-bold">{clipVolume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={clipVolume}
                  onChange={(e) => setClipVolume(parseInt(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-300 font-medium">Volumen de la Pista Musical</span>
                  <span className="text-pink-400 font-mono font-bold">{musicVolume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  value={musicVolume}
                  onChange={(e) => setMusicVolume(parseInt(e.target.value))}
                  className="w-full accent-pink-500 cursor-pointer"
                />
              </div>
            </div>

            <button
              onClick={() => setShowMixerModal(false)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-xs shadow-md shadow-pink-500/20"
            >
              Guardar Ajustes de Audio
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
