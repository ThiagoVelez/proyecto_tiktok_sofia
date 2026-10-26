/**
 * Barra de Navegacion Principal Superior de Follow.
 * Incluye menu flotante de perfil (Cerrar sesion, Configurar), modal de Ajustes funcionales
 * y modal interactivo de Mensajes Directos (DM).
 */

import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Search, Plus, Send, Bell, User, Settings, LogOut, 
  Sparkles 
} from 'lucide-react';
import { DirectMessagesModal } from '../chat/DirectMessagesModal';
import { SettingsModal } from '../settings/SettingsModal';
import { clearAuthSession } from '../../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isMessagesOpen, setIsMessagesOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/explorar?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/explorar');
    }
  };

  // Cerrar menu al hacer clic fuera o presionar Escape
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const handleLogout = () => {
    clearAuthSession();
    setIsProfileMenuOpen(false);
    navigate('/login');
  };

  return (
    <>
      <header className="sticky top-0 z-50 w-full bg-[#0c0d14]/90 backdrop-blur-md border-b border-white/5 px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          
          {/* LOGO Y ENLACES PRINCIPALES */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-rose-400 flex items-center justify-center shadow-lg shadow-pink-500/20 group-hover:scale-105 transition-transform">
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m22 2-7 20-4-9-9-4Z" />
                  <path d="M22 2 11 13" />
                </svg>
              </div>
              <span className="text-xl font-bold tracking-tight text-white font-sans">Follow</span>
            </Link>

            {/* Menu de Navegacion Desktop */}
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
              <Link
                to="/"
                className={`transition-colors hover:text-white ${
                  isActive('/') ? 'text-white font-semibold' : 'text-gray-400'
                }`}
              >
                Feed
              </Link>
              <Link
                to="/explorar"
                className={`transition-colors hover:text-white ${
                  isActive('/explorar') ? 'text-white font-semibold' : 'text-gray-400'
                }`}
              >
                Explorar
              </Link>
              <Link
                to="/tendencias"
                className={`transition-colors hover:text-white ${
                  isActive('/tendencias') ? 'text-white font-semibold' : 'text-gray-400'
                }`}
              >
                Tendencias
              </Link>
              <Link
                to="/en-vivo"
                className={`transition-colors hover:text-white ${
                  isActive('/en-vivo') ? 'text-white font-semibold' : 'text-gray-400'
                }`}
              >
                En Vivo
              </Link>
            </nav>
          </div>

          {/* BARRA DE BUSQUEDA CENTRAL */}
          <div className="flex-1 max-w-md hidden sm:block">
            <form onSubmit={handleSearchSubmit} className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                <Search className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar creadores, sonidos y hashtags..."
                className="w-full bg-[#181a27] border border-white/5 rounded-full pl-10 pr-10 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50 focus:ring-1 focus:ring-pink-500/50 transition-all"
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <kbd className="px-1.5 py-0.5 text-[10px] text-gray-400 bg-white/5 rounded border border-white/10 font-mono">
                  /
                </kbd>
              </div>
            </form>
          </div>

          {/* ACCIONES Y PERFIL DE USUARIO */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Boton + Crear (visible en pantallas medianas y grandes, en movil reside en BottomNav) */}
            <Link
              to="/estudio"
              className="hidden sm:flex items-center gap-1.5 px-4 py-2 rounded-full bg-gradient-to-r from-purple-600 via-pink-600 to-rose-500 text-white text-xs font-semibold shadow-lg shadow-pink-500/20 hover:brightness-110 active:scale-95 transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Crear</span>
            </Link>

            {/* Mensajes Directos (Abre modal de DMs) */}
            <button
              type="button"
              onClick={() => setIsMessagesOpen(true)}
              aria-label="Mensajes directos"
              className="p-2 text-gray-300 hover:text-white rounded-full hover:bg-white/5 transition-colors relative active:scale-95"
            >
              <Send className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-[#0c0d14]"></span>
            </button>

            {/* Notificaciones / Actividad */}
            <Link
              to="/actividad"
              aria-label="Notificaciones"
              className="p-2 text-gray-300 hover:text-white rounded-full hover:bg-white/5 transition-colors relative active:scale-95"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-pink-500 ring-2 ring-[#0c0d14]"></span>
            </Link>

            {/* Avatar del usuario con Menu Desplegable Interactivo */}
            <div className="relative ml-0.5" ref={profileMenuRef}>
              <button
                type="button"
                onClick={() => setIsProfileMenuOpen(prev => !prev)}
                aria-expanded={isProfileMenuOpen}
                aria-label="Menu de perfil y ajustes"
                className="relative flex items-center justify-center p-0.5 rounded-full ring-2 ring-pink-500/40 hover:ring-pink-500 focus:outline-none transition-all cursor-pointer active:scale-95"
              >
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100"
                  alt="Valeria Gomez"
                  className="w-7 h-7 rounded-full object-cover"
                />
              </button>

              {/* Menu flotante de perfil */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 top-full mt-2.5 w-72 max-w-[calc(100vw-2rem)] rounded-2xl bg-[#141524] border border-white/10 shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                  {/* Cabecera del usuario */}
                  <div className="flex items-center gap-3 p-2.5 rounded-xl bg-white/5 border border-white/5">
                    <img
                      src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100"
                      alt="Valeria Gomez"
                      className="w-10 h-10 rounded-full object-cover border border-pink-500/40"
                    />
                    <div className="overflow-hidden">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-white truncate">Valeria Gomez</span>
                        <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.2 bg-purple-900/60 text-purple-300 border border-purple-500/30 rounded">
                          PRO
                        </span>
                      </div>
                      <span className="text-[11px] text-gray-400 block truncate">@valeria_creatrix</span>
                      <span className="text-[10px] text-cyan-400 block truncate">valeria@follow.io</span>
                    </div>
                  </div>

                  <div className="h-px bg-white/10 my-1.5" />

                  {/* Opciones del menu */}
                  <div className="space-y-0.5 text-xs font-medium">
                    <Link
                      to="/perfil"
                      onClick={() => setIsProfileMenuOpen(false)}
                      className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-gray-200 hover:text-white hover:bg-white/10 transition-colors"
                    >
                      <User className="w-4 h-4 text-cyan-400" />
                      <span>Ver mi perfil</span>
                    </Link>

                    <Link
                      to="/estudio"
                      onClick={() => setIsProfileMenuOpen(false)}
                      className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-gray-200 hover:text-white hover:bg-white/10 transition-colors"
                    >
                      <Sparkles className="w-4 h-4 text-pink-400" />
                      <span>Creator Studio & Metricas</span>
                    </Link>

                    {/* Boton Configurar con todo el apartado funcional */}
                    <button
                      type="button"
                      onClick={() => {
                        setIsProfileMenuOpen(false);
                        setIsSettingsOpen(true);
                      }}
                      className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-gray-200 hover:text-white hover:bg-white/10 transition-colors text-left"
                    >
                      <Settings className="w-4 h-4 text-purple-400" />
                      <span>Configurar</span>
                    </button>
                  </div>

                  <div className="h-px bg-white/10 my-1.5" />

                  {/* Boton Cerrar Sesion */}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-rose-300 hover:text-white hover:bg-rose-600/20 border border-transparent hover:border-rose-500/30 text-xs font-bold transition-all text-left"
                  >
                    <LogOut className="w-4 h-4 text-rose-400" />
                    <span>Cerrar sesion</span>
                  </button>
                </div>
              )}
            </div>
          </div>

        </div>
      </header>

      {/* Modal interactivo de Mensajes Directos */}
      <DirectMessagesModal
        isOpen={isMessagesOpen}
        onClose={() => setIsMessagesOpen(false)}
      />

      {/* Modal Funcional Completo de Configuracion */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </>
  );
};
