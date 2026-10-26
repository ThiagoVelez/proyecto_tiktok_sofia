/**
 * Pantalla de Actividad y Notificaciones (Follow Activity).
 * Registro completo de interacciones: Me Gusta, Comentarios, Nuevos Seguidores y Menciones.
 */

import React, { useState } from 'react';
import { 
  Heart, MessageSquare, UserPlus, AtSign, CheckCheck, 
  Sparkles, Filter, Bell, ChevronRight, Play
} from 'lucide-react';

interface ActivityItem {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'mention';
  user: string;
  userAvatar: string;
  description: string;
  time: string;
  videoThumb?: string;
  isUnread?: boolean;
  isFollowing?: boolean;
}

export const ActivityPage: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'likes' | 'comments' | 'followers' | 'mentions'>('all');

  const [activities, setActivities] = useState<ActivityItem[]>([
    {
      id: '1',
      type: 'like',
      user: 'mateo_vfx',
      userAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100',
      description: 'le gusto tu publicacion "Configurando el nuevo setup holografico..."',
      time: 'Hace 5m',
      videoThumb: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=100',
      isUnread: true
    },
    {
      id: '2',
      type: 'follow',
      user: 'clara_design',
      userAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100',
      description: 'ha comenzado a seguirte',
      time: 'Hace 28m',
      isUnread: true,
      isFollowing: false
    },
    {
      id: '3',
      type: 'comment',
      user: 'dev_raul',
      userAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100',
      description: 'comento: "Increible render. Cuanto tardo en exportar ese tracking de camara?"',
      time: 'Hace 1h',
      videoThumb: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=100',
      isUnread: false
    },
    {
      id: '4',
      type: 'mention',
      user: 'alex_neon',
      userAvatar: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=100',
      description: 'te menciono como colaboradora en "Modding de sintetizadores analogicos..."',
      time: 'Hace 2h',
      videoThumb: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=100',
      isUnread: false
    },
    {
      id: '5',
      type: 'like',
      user: 'kira_techwear',
      userAvatar: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=100',
      description: 'le gusto tu video "Cyberpunk Street Wear 2025"',
      time: 'Hace 4h',
      videoThumb: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=100',
      isUnread: false
    },
    {
      id: '6',
      type: 'follow',
      user: 'neo_shibuya',
      userAvatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100',
      description: 'ha comenzado a seguirte',
      time: 'Ayer',
      isUnread: false,
      isFollowing: true
    }
  ]);

  const markAllAsRead = () => {
    setActivities(prev => prev.map(a => ({ ...a, isUnread: false })));
  };

  const toggleFollowBack = (id: string) => {
    setActivities(prev => prev.map(a => a.id === id ? { ...a, isFollowing: !a.isFollowing } : a));
  };

  const filtered = activities.filter(a => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'likes') return a.type === 'like';
    if (activeFilter === 'comments') return a.type === 'comment';
    if (activeFilter === 'followers') return a.type === 'follow';
    if (activeFilter === 'mentions') return a.type === 'mention';
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0c0d14] text-white pb-28 pt-4 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-6">
      
      {/* CABECERA DE ACTIVIDAD */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-pink-600 to-purple-600 flex items-center justify-center shadow-lg shadow-pink-500/25">
            <Heart className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-white">Actividad</h1>
            <span className="text-xs text-gray-400">Notificaciones e interacciones directas con tu cuenta</span>
          </div>
        </div>

        <button
          onClick={markAllAsRead}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-gray-300 hover:text-white border border-white/5 self-start sm:self-auto transition-colors"
        >
          <CheckCheck className="w-4 h-4 text-cyan-400" />
          <span>Marcar todo como leido</span>
        </button>
      </div>

      {/* PILDORAS DE FILTRADO */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none text-xs font-semibold">
        {[
          { key: 'all', label: 'Todas' },
          { key: 'likes', label: 'Me Gusta' },
          { key: 'comments', label: 'Comentarios' },
          { key: 'followers', label: 'Seguidores' },
          { key: 'mentions', label: 'Menciones' }
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setActiveFilter(f.key as any)}
            className={`px-4 py-1.5 rounded-full transition-all ${
              activeFilter === f.key
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                : 'bg-[#151624] text-gray-400 hover:text-white border border-white/5'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* LISTA DE NOTIFICACIONES / ACTIVIDADES */}
      <div className="space-y-2.5">
        {filtered.map((item) => (
          <div
            key={item.id}
            className={`p-4 rounded-2xl border transition-all flex items-center justify-between gap-4 ${
              item.isUnread
                ? 'bg-[#18192a] border-pink-500/30 shadow-md shadow-pink-500/5'
                : 'bg-[#131422] border-white/5 hover:border-white/10'
            }`}
          >
            <div className="flex items-center gap-3 min-w-0">
              
              {/* Avatar con icono de accion superpuesto */}
              <div className="relative flex-shrink-0">
                <img
                  src={item.userAvatar}
                  alt=""
                  className="w-11 h-11 rounded-full object-cover border border-white/10"
                />
                <span className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] text-white border border-[#0c0d14] ${
                  item.type === 'like' ? 'bg-rose-500' :
                  item.type === 'comment' ? 'bg-cyan-500' :
                  item.type === 'follow' ? 'bg-purple-600' : 'bg-pink-500'
                }`}>
                  {item.type === 'like' && <Heart className="w-2.5 h-2.5 fill-white" />}
                  {item.type === 'comment' && <MessageSquare className="w-2.5 h-2.5 fill-white" />}
                  {item.type === 'follow' && <UserPlus className="w-2.5 h-2.5" />}
                  {item.type === 'mention' && <AtSign className="w-2.5 h-2.5" />}
                </span>
              </div>

              {/* Texto de la notificacion */}
              <div className="text-xs space-y-0.5 min-w-0">
                <p className="text-gray-200 leading-snug">
                  <span className="font-bold text-white pr-1">@{item.user}</span>
                  <span>{item.description}</span>
                </p>
                <div className="flex items-center gap-2 text-[10px] text-gray-500">
                  <span>{item.time}</span>
                  {item.isUnread && (
                    <span className="w-1.5 h-1.5 rounded-full bg-pink-500"></span>
                  )}
                </div>
              </div>

            </div>

            {/* Accion o Miniatura a la derecha */}
            <div className="flex-shrink-0">
              {item.videoThumb ? (
                <div className="relative w-11 h-14 rounded-xl overflow-hidden bg-black border border-white/10">
                  <img src={item.videoThumb} alt="" className="w-full h-full object-cover" />
                </div>
              ) : item.type === 'follow' ? (
                <button
                  onClick={() => toggleFollowBack(item.id)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    item.isFollowing
                      ? 'bg-white/10 text-gray-300'
                      : 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-md shadow-pink-500/20 hover:brightness-110'
                  }`}
                >
                  {item.isFollowing ? 'Siguiendo' : 'Seguir tambien'}
                </button>
              ) : null}
            </div>

          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-500 space-y-2">
            <Bell className="w-8 h-8 mx-auto opacity-30" />
            <p className="text-xs">No hay actividad registrada en esta categoria.</p>
          </div>
        )}
      </div>

    </div>
  );
};
