/**
 * Pantalla de Transmisiones En Vivo (Follow Live).
 * Streaming vertical con chat interactivo en tiempo real, lluvia de reacciones y cambio de salas.
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Radio, Eye, Heart, Send, Volume2, VolumeX, Sparkles, 
  Trophy, Zap, Share2, CheckCircle, Plus, Users, 
  MessageSquare, Maximize2, Shield
} from 'lucide-react';

interface LiveRoom {
  id: string;
  title: string;
  creator: string;
  creatorAvatar: string;
  viewers: string;
  category: string;
  streamUrl: string;
  cover: string;
}

interface ChatMessage {
  id: number;
  user: string;
  avatar: string;
  message: string;
  badge?: string;
  time: string;
}

export const LivePage: React.FC = () => {
  const [isMuted, setIsMuted] = useState(false);
  const [likesCount, setLikesCount] = useState(1420800);
  const [burstHearts, setBurstHearts] = useState<number[]>([]);
  const [chatInput, setChatInput] = useState('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Salas de streaming disponibles
  const rooms: LiveRoom[] = [
    {
      id: '1',
      title: "Explorando nuevas frecuencias visuales en el showcase nocturno de Tokio",
      creator: "@sofia.k",
      creatorAvatar: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100",
      viewers: "42.8k",
      category: "Arte & Musica",
      streamUrl: "/videos/cyber_street.mp4",
      cover: "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600"
    },
    {
      id: '2',
      title: "Tokyo Techwear Week 2025: Pasarela subterranea y textiles inteligentes",
      creator: "@tokyofashion_tv",
      creatorAvatar: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=100",
      viewers: "12.6k",
      category: "Moda Cyberpunk",
      streamUrl: "/videos/fashion_walk.mp4",
      cover: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600"
    },
    {
      id: '3',
      title: "Modding de sintetizadores analogicos y efectos laser en directo",
      creator: "@alex_neon",
      creatorAvatar: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=100",
      viewers: "8.4k",
      category: "Hardware & Tech",
      streamUrl: "/videos/city_traffic.mp4",
      cover: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600"
    }
  ];

  const [activeRoom, setActiveRoom] = useState<LiveRoom>(rooms[0]);

  // Mensajes de chat en vivo
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, user: "mateo_vfx", avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50", message: "Esos visuales reactivos al bajo estan brutales!", badge: "TOP FAN", time: "16:20" },
    { id: 2, user: "clara_design", avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50", message: "Que lente estas usando para ese bokeh anamorfico?", time: "16:21" },
    { id: 3, user: "kira_techwear", avatar: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=50", message: "Saludos desde Shibuya! La conexion se ve perfecta a 4K.", badge: "MOD", time: "16:21" },
    { id: 4, user: "dev_raul", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50", message: "Manda un saludo a la comunidad de Madrid!", time: "16:22" }
  ]);

  // Auto-scroll del chat al ingresar nuevos mensajes
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendLiveComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const newMsg: ChatMessage = {
      id: Date.now(),
      user: "marcos.creator",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50",
      message: chatInput.trim(),
      badge: "VIP",
      time: "Ahora"
    };

    setMessages(prev => [...prev, newMsg]);
    setChatInput('');
  };

  const handleHeartReaction = () => {
    setLikesCount(c => c + 1);
    setBurstHearts(prev => [...prev.slice(-10), Date.now()]);
  };

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      
      {/* CABECERA DE LA SALA EN VIVO */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-purple-600 flex items-center justify-center shadow-lg shadow-rose-500/25">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-white">Transmisiones en Vivo</h1>
              <span className="px-2 py-0.5 rounded-md bg-rose-600 text-white font-extrabold text-[10px] uppercase tracking-wider">
                LIVE
              </span>
            </div>
            <span className="text-xs text-gray-400">Canales verificados emitiendo en 4K Ultra HD y baja latencia</span>
          </div>
        </div>

        {/* Metadatos tecnicos */}
        <div className="flex items-center gap-3 bg-[#141524] px-4 py-2 rounded-2xl border border-white/5 text-xs text-gray-300 font-mono">
          <span className="flex items-center gap-1.5 text-cyan-400 font-semibold">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            18ms LATENCIA
          </span>
          <span className="text-gray-600">•</span>
          <span>4K HDR 60FPS</span>
        </div>
      </div>

      {/* CONTENEDOR PRINCIPAL: STREAMING A LA IZQUIERDA Y CHAT EN DIRECTO A LA DERECHA */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* REPRODUCTOR EN VIVO (8 COLUMNAS) */}
        <div className="lg:col-span-8 space-y-4">
          
          <div className="relative aspect-video w-full rounded-3xl overflow-hidden bg-black border border-white/10 shadow-2xl flex flex-col justify-between p-4 group">
            
            {/* Video del Stream */}
            <video
              src={activeRoom.streamUrl}
              autoPlay
              loop
              muted={isMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-transparent to-black/60 pointer-events-none"></div>

            {/* Cabecera del Stream */}
            <div className="relative z-10 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2.5">
                <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10">
                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                  <span className="text-rose-400 font-bold uppercase text-[10px] tracking-wider">EN DIRECTO</span>
                  <span className="text-white font-mono font-bold text-xs">{activeRoom.viewers}</span>
                </div>

                <span className="hidden sm:inline-block px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-[11px] text-gray-300">
                  {activeRoom.category}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-2 rounded-full bg-black/60 backdrop-blur-md text-white hover:bg-black/80 transition-colors"
                >
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>
                <button className="p-2 rounded-full bg-black/60 backdrop-blur-md text-white hover:bg-black/80 transition-colors">
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Particulas de Corazones Flotantes */}
            <div className="absolute right-6 bottom-20 z-20 pointer-events-none">
              {burstHearts.map((timeKey) => (
                <div
                  key={timeKey}
                  className="absolute bottom-0 right-0 animate-bounce text-rose-500 opacity-90"
                  style={{ animationDuration: '1.2s' }}
                >
                  <Heart className="w-7 h-7 fill-rose-500" />
                </div>
              ))}
            </div>

            {/* Barra Inferior del Stream: Creador, Titulo y Acciones */}
            <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <img
                  src={activeRoom.creatorAvatar}
                  alt=""
                  className="w-11 h-11 rounded-full border-2 border-pink-500 object-cover"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{activeRoom.creator}</span>
                    <CheckCircle className="w-4 h-4 text-cyan-400 fill-cyan-400/20" />
                    <button className="px-3 py-0.5 rounded-full bg-pink-600 text-white text-[10px] font-bold uppercase tracking-wider hover:bg-pink-500 transition-colors">
                      SEGUIR
                    </button>
                  </div>
                  <h3 className="text-xs text-gray-200 font-medium line-clamp-1 max-w-md pt-0.5">
                    {activeRoom.title}
                  </h3>
                </div>
              </div>

              {/* Boton de Reaccion Me Gusta */}
              <div className="flex items-center gap-2 self-end sm:self-auto">
                <button
                  onClick={handleHeartReaction}
                  className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-rose-600/30 hover:bg-rose-600/40 border border-rose-500/40 text-rose-300 font-bold text-xs shadow-lg shadow-rose-500/20 active:scale-95 transition-all"
                >
                  <Heart className="w-4 h-4 fill-rose-400 text-rose-400" />
                  <span>{(likesCount / 1000000).toFixed(2)}M</span>
                </button>

                <button className="p-2 rounded-2xl bg-white/10 hover:bg-white/20 text-white border border-white/10">
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </div>

          </div>

          {/* OTRAS SALAS EN VIVO RECOMENDADAS */}
          <div className="pt-2 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-pink-400" />
              <span>Otras transmisiones activas</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {rooms.filter(r => r.id !== activeRoom.id).map((r) => (
                <div
                  key={r.id}
                  onClick={() => setActiveRoom(r)}
                  className="p-3 rounded-2xl bg-[#141524] border border-white/5 hover:border-pink-500/40 cursor-pointer transition-all flex items-center gap-3 group"
                >
                  <div className="relative w-20 aspect-video rounded-xl overflow-hidden bg-black flex-shrink-0">
                    <img src={r.cover} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                    <span className="absolute bottom-1 right-1 px-1 rounded bg-rose-600 text-white text-[8px] font-bold">
                      LIVE
                    </span>
                  </div>
                  <div className="overflow-hidden space-y-0.5">
                    <span className="text-[10px] text-cyan-400 font-bold">{r.category}</span>
                    <h4 className="text-xs font-bold text-white truncate block">{r.title}</h4>
                    <span className="text-[10px] text-gray-400 block">{r.creator} • {r.viewers} espectadores</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* CHAT EN DIRECTO (4 COLUMNAS) */}
        <div className="lg:col-span-4 bg-[#141524] rounded-3xl border border-white/5 p-4 flex flex-col justify-between h-[520px]">
          
          {/* Cabecera del Chat */}
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Chat en Directo</h3>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-gray-400">
              <Shield className="w-3.5 h-3.5 text-emerald-400" />
              <span>Filtro activo</span>
            </div>
          </div>

          {/* Area de mensajes con scroll */}
          <div ref={chatContainerRef} className="flex-1 overflow-y-auto py-3 space-y-3 pr-1">
            {messages.map((m) => (
              <div key={m.id} className="text-xs space-y-0.5">
                <div className="flex items-center gap-2">
                  <img src={m.avatar} alt="" className="w-5 h-5 rounded-full object-cover border border-white/10" />
                  <span className="font-bold text-gray-300">{m.user}</span>
                  {m.badge && (
                    <span className="text-[8px] font-extrabold uppercase px-1.5 rounded bg-purple-900/60 text-purple-300 border border-purple-500/30">
                      {m.badge}
                    </span>
                  )}
                  <span className="text-[9px] text-gray-500 ml-auto">{m.time}</span>
                </div>
                <p className="text-gray-200 text-xs pl-7 leading-snug">{m.message}</p>
              </div>
            ))}
          </div>

          {/* Botones de Recompensas / Apoyo */}
          <div className="py-2 border-t border-white/5 flex items-center justify-between text-xs text-gray-300">
            <span className="text-[10px] text-gray-500 uppercase font-mono">Apoyar:</span>
            <div className="flex items-center gap-2">
              <button className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-white/5 hover:bg-yellow-500/20 text-yellow-300 text-[10px] font-semibold border border-white/5">
                <Trophy className="w-3 h-3" />
                <span>Trofeo</span>
              </button>
              <button className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-white/5 hover:bg-cyan-500/20 text-cyan-300 text-[10px] font-semibold border border-white/5">
                <Zap className="w-3 h-3" />
                <span>Rayo</span>
              </button>
              <button className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-white/5 hover:bg-pink-500/20 text-pink-300 text-[10px] font-semibold border border-white/5">
                <Sparkles className="w-3 h-3" />
                <span>Gema</span>
              </button>
            </div>
          </div>

          {/* Formulario para Enviar Mensaje al Chat */}
          <form onSubmit={handleSendLiveComment} className="relative pt-1">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Envia un mensaje en el directo..."
              className="w-full bg-[#1b1c2e] border border-white/10 rounded-2xl pl-4 pr-11 py-2.5 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
            />
            <button
              type="submit"
              disabled={!chatInput.trim()}
              className="absolute right-1.5 top-2.5 p-1.5 rounded-xl bg-cyan-500 text-black font-bold disabled:opacity-40 transition-opacity"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>

        </div>

      </div>

    </div>
  );
};
