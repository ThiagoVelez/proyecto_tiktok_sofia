/**
 * Barra de Navegacion Flotante Inferior de Follow (Mobile / Floating Dock).
 * Conexiones completas a Para Ti (/), Explorar (/explorar), Crear (/estudio), Actividad (/actividad) y Perfil (/perfil).
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Compass, Plus, Heart, User } from 'lucide-react';

export const BottomNav: React.FC = () => {
  const location = useLocation();

  const isCurrent = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <div className="fixed bottom-[max(0.75rem,env(safe-area-inset-bottom))] left-1/2 -translate-x-1/2 z-40 w-auto max-w-[calc(100vw-1rem)]">
      <nav className="flex items-center justify-between sm:justify-center gap-1 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-[#181926]/95 backdrop-blur-2xl border border-white/10 shadow-2xl shadow-black/90 select-none">
        
        {/* Para ti */}
        <Link
          to="/"
          aria-label="Feed Para ti"
          className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-2 rounded-full min-h-[40px] text-xs transition-all active:scale-95 ${
            isCurrent('/')
              ? 'text-white bg-white/10 font-medium'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Home className="w-4 h-4 flex-shrink-0" />
          <span className="text-[11px] hidden xs:inline">Para ti</span>
        </Link>

        {/* Explorar */}
        <Link
          to="/explorar"
          aria-label="Explorar"
          className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-2 rounded-full min-h-[40px] text-xs transition-all active:scale-95 ${
            isCurrent('/explorar')
              ? 'text-white bg-white/10 font-medium'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Compass className="w-4 h-4 flex-shrink-0" />
          <span className="text-[11px] hidden xs:inline">Explorar</span>
        </Link>

        {/* Boton Central + Crear */}
        <Link
          to="/estudio"
          aria-label="Crear publicacion"
          className="mx-0.5 sm:mx-1 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-r from-purple-500 via-pink-500 to-rose-400 flex items-center justify-center text-white shadow-lg shadow-pink-500/30 hover:scale-105 active:scale-90 transition-transform flex-shrink-0"
        >
          <Plus className="w-5 h-5 stroke-[2.5]" />
        </Link>

        {/* Actividad */}
        <Link
          to="/actividad"
          aria-label="Actividad y notificaciones"
          className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-2 rounded-full min-h-[40px] text-xs transition-all active:scale-95 ${
            isCurrent('/actividad')
              ? 'text-white bg-white/10 font-medium'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Heart className={`w-4 h-4 flex-shrink-0 ${isCurrent('/actividad') ? 'fill-pink-500 text-pink-500' : ''}`} />
          <span className="text-[11px] hidden xs:inline">Actividad</span>
        </Link>

        {/* Perfil */}
        <Link
          to="/perfil"
          aria-label="Mi Perfil"
          className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-2 rounded-full min-h-[40px] text-xs transition-all active:scale-95 ${
            isCurrent('/perfil')
              ? 'text-white bg-white/10 font-medium'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <User className="w-4 h-4 flex-shrink-0" />
          <span className="text-[11px] hidden xs:inline">Perfil</span>
        </Link>

      </nav>
    </div>
  );
};
