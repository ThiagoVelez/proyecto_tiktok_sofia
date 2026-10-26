/**
 * Pantalla 2: Autenticación, Login y Registro (Follow Auth).
 * Replicación exacta del diseño de Stitch con previsualización en vivo.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Volume2, VolumeX, Heart, MessageSquare, Share2, 
  Plus, CheckCircle, Shield, Eye, EyeOff, Lock, AtSign, 
  ArrowRight, Radio, Activity
} from 'lucide-react';
import { login } from '../services/api';

export const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [liked, setLiked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err: unknown) {
      const error = err as Error;
      setErrorMsg(error.message || 'Error al autenticar.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a10] text-white flex flex-col justify-between p-4 sm:p-6 lg:p-8">
      
      {/* BARRA SUPERIOR DE ESTADO PULSE */}
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between py-2 text-xs">
        {/* Pulse Version */}
        <div className="flex items-center gap-2 bg-[#12131d] px-3 py-1 rounded-full border border-white/5">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span className="text-gray-300 font-mono tracking-wider text-[11px]">FOLLOW PULSE V2.4</span>
        </div>

        {/* BPM & Viral Radar */}
        <div className="flex items-center gap-2 bg-[#12131d] px-3.5 py-1 rounded-full border border-white/5 text-gray-400 font-mono text-[11px]">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>BPM: 132</span>
          <span className="text-gray-600">•</span>
          <span className="text-cyan-400 font-semibold tracking-wider">VIRAL RADAR ACTIVE</span>
        </div>
      </div>

      {/* CONTENEDOR PRINCIPAL DOS COLUMNAS */}
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center my-auto py-6">
        
        {/* COLUMNA IZQUIERDA: MOCKUP SMARTPHONE STREAMING EN VIVO (Visible en pantallas medianas y superiores) */}
        <div className="lg:col-span-6 hidden md:flex flex-col items-center">
          <div className="relative w-full max-w-[340px] aspect-[9/18] rounded-[38px] p-2.5 bg-gradient-to-b from-[#24273d] to-[#12131d] shadow-2xl shadow-purple-950/40 border border-white/10 overflow-hidden">
            
            {/* Pantalla interna del teléfono */}
            <div className="relative w-full h-full rounded-[30px] overflow-hidden bg-black flex flex-col justify-between p-4">
              
              {/* Video de fondo simulado */}
              <img
                src="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800"
                alt="Sofia K en Directo"
                className="absolute inset-0 w-full h-full object-cover brightness-95 contrast-110"
              />
              <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/90 pointer-events-none"></div>

              {/* Cabecera del Directo */}
              <div className="relative z-10 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-2.5 py-1 rounded-full border border-white/10">
                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                  <span className="text-rose-400 font-bold uppercase text-[10px]">EN DIRECTO</span>
                  <span className="text-gray-300 font-medium text-[10px]">42.8k</span>
                </div>

                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-1.5 rounded-full bg-black/40 backdrop-blur-md text-white hover:bg-black/60 transition-colors"
                >
                  {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                </button>
              </div>

              {/* Card Flotante: Sonido Viral */}
              <div className="absolute top-24 right-3 z-10 bg-[#161826]/90 backdrop-blur-md p-2 rounded-xl border border-white/10 flex items-center gap-2 shadow-lg max-w-[190px]">
                <div className="w-7 h-7 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0">
                  <Radio className="w-4 h-4 animate-pulse" />
                </div>
                <div className="overflow-hidden text-[10px]">
                  <span className="text-cyan-400 font-bold block uppercase text-[8px] tracking-wider">SONIDO VIRAL</span>
                  <span className="text-white font-semibold truncate block">Neon Horizon Beat</span>
                  <span className="text-gray-400 text-[9px]">1.8M reproducciones</span>
                </div>
              </div>

              {/* Badges y Columna de Acciones Flotantes */}
              <div className="relative z-10 flex items-end justify-between">
                
                {/* Lado izquierdo inferior: Trending Studio & Datos del Creador */}
                <div className="space-y-2 max-w-[210px]">
                  {/* Trending Pill */}
                  <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md p-1.5 rounded-xl border border-white/10">
                    <img
                      src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100"
                      alt="Kaelo Studio"
                      className="w-6 h-6 rounded-lg object-cover"
                    />
                    <div className="text-[10px]">
                      <div className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                        <span className="text-rose-300 font-bold text-[8px] uppercase">TRENDING #1</span>
                      </div>
                      <span className="text-white font-bold block leading-tight">Kaelo Studio</span>
                      <span className="text-gray-400 text-[8px]">+380K remixes hoy</span>
                    </div>
                  </div>

                  {/* Creador y Descripción */}
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-white font-bold text-xs">@sofia.k</span>
                      <CheckCircle className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />
                      <button className="text-[9px] font-bold text-gray-300 bg-white/20 hover:bg-white/30 px-2 py-0.5 rounded-full uppercase">
                        SEGUIR
                      </button>
                    </div>
                    <p className="text-[10px] text-gray-300 line-clamp-2 mt-0.5 leading-tight">
                      Explorando nuevas frecuencias visuales en el showcase nocturno de Tokio...
                    </p>
                  </div>

                  {/* Sonido actual */}
                  <div className="flex items-center gap-1.5 text-[9px] text-cyan-300 bg-black/40 px-2 py-0.5 rounded-full backdrop-blur-sm">
                    <Radio className="w-3 h-3 text-cyan-400" />
                    <span className="truncate">Sofia K • Cyber Night ...</span>
                  </div>

                  {/* Barra de progreso */}
                  <div className="w-full bg-white/20 h-0.5 rounded-full overflow-hidden">
                    <div className="w-2/3 h-full bg-pink-500 rounded-full"></div>
                  </div>
                </div>

                {/* Columna Derecha: Acciones Interactivas */}
                <div className="flex flex-col items-center gap-3">
                  {/* Avatar con botón seguir */}
                  <div className="relative">
                    <img
                      src="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100"
                      alt="Sofia"
                      className="w-8 h-8 rounded-full border border-pink-500 object-cover"
                    />
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full bg-pink-500 text-white flex items-center justify-center">
                      <Plus className="w-2.5 h-2.5 stroke-[3]" />
                    </div>
                  </div>

                  {/* Like */}
                  <button onClick={() => setLiked(!liked)} className="flex flex-col items-center gap-0.5">
                    <div className={`p-2 rounded-full ${liked ? 'bg-rose-500/30 text-rose-400' : 'bg-black/50 text-white'} backdrop-blur-md`}>
                      <Heart className={`w-4 h-4 ${liked ? 'fill-rose-400 text-rose-400' : ''}`} />
                    </div>
                    <span className="text-[9px] font-semibold text-white">1.4M</span>
                  </button>

                  {/* Comentarios */}
                  <div className="flex flex-col items-center gap-0.5">
                    <div className="p-2 rounded-full bg-black/50 text-white backdrop-blur-md">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <span className="text-[9px] font-semibold text-white">18.2K</span>
                  </div>

                  {/* Compartir */}
                  <div className="flex flex-col items-center gap-0.5">
                    <div className="p-2 rounded-full bg-black/50 text-white backdrop-blur-md">
                      <Share2 className="w-4 h-4" />
                    </div>
                    <span className="text-[9px] font-semibold text-white">9.7K</span>
                  </div>
                </div>

              </div>

            </div>
          </div>

          {/* Badges de credibilidad debajo del teléfono */}
          <div className="flex items-center gap-4 mt-6">
            <div className="flex items-center gap-2.5 bg-[#12131d] px-3.5 py-2 rounded-2xl border border-white/5">
              <div className="flex -space-x-1.5">
                <img className="w-5 h-5 rounded-full border border-black object-cover" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50" alt="" />
                <img className="w-5 h-5 rounded-full border border-black object-cover" src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50" alt="" />
                <img className="w-5 h-5 rounded-full border border-black object-cover" src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50" alt="" />
              </div>
              <div className="text-[10px]">
                <span className="font-bold text-white block">Únete a más de 120M de creadores</span>
                <span className="text-gray-400 text-[9px]">Monetización instantánea & streaming 4K HDR</span>
              </div>
            </div>

            <div className="bg-[#12131d] px-3 py-2 rounded-2xl border border-white/5 flex items-center gap-2 text-[10px]">
              <span className="text-gray-400 font-mono uppercase">LATENCIA 18ms</span>
              <div className="flex items-end gap-0.5 h-3">
                <span className="w-0.5 h-1.5 bg-cyan-400 rounded-full"></span>
                <span className="w-0.5 h-2 bg-pink-500 rounded-full"></span>
                <span className="w-0.5 h-3 bg-purple-500 rounded-full"></span>
              </div>
            </div>
          </div>

        </div>

        {/* COLUMNA DERECHA: FORMULARIO DE INICIO DE SESIÓN */}
        <div className="lg:col-span-6 max-w-md w-full mx-auto space-y-6">
          
          {/* Cabecera del formulario */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-rose-400 flex items-center justify-center shadow-lg shadow-pink-500/20">
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="m22 2-7 20-4-9-9-4Z" />
                  <path d="M22 2 11 13" />
                </svg>
              </div>
              <div>
                <span className="text-xl font-bold tracking-tight text-white block">Follow •</span>
                <span className="text-[9px] font-extrabold uppercase tracking-widest text-pink-400 block -mt-1">
                  NEXT-GEN VIDEO PLATFORM
                </span>
              </div>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed pt-1">
              Entra a tu feed personalizado, conecta en vivo y comparte tu visión con el mundo.
            </p>
          </div>

          {/* Toggle Iniciar Sesión / Registrarse */}
          <div className="grid grid-cols-2 p-1 bg-[#151624] rounded-2xl border border-white/5 text-xs font-semibold">
            <button
              onClick={() => setMode('login')}
              className={`py-2.5 rounded-xl transition-all ${
                mode === 'login'
                  ? 'bg-[#23263b] text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => setMode('register')}
              className={`py-2.5 rounded-xl transition-all ${
                mode === 'register'
                  ? 'bg-[#23263b] text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Registrarse
            </button>
          </div>

          {/* Botones de Redes Sociales */}
          <div className="grid grid-cols-4 gap-2.5">
            {['Google', 'Apple', 'TikTok', 'X'].map((brand) => (
              <button
                key={brand}
                type="button"
                className="flex items-center justify-center py-2.5 rounded-xl bg-[#151624] hover:bg-[#1f2136] border border-white/5 text-gray-300 hover:text-white text-xs font-semibold transition-colors"
              >
                {brand === 'Google' && <span className="font-bold text-rose-400">G</span>}
                {brand === 'Apple' && <span className="font-bold"></span>}
                {brand === 'TikTok' && <span className="font-bold text-cyan-400">d</span>}
                {brand === 'X' && <span className="font-bold">𝕏</span>}
              </button>
            ))}
          </div>

          {/* Separador */}
          <div className="relative flex items-center justify-center">
            <div className="w-full border-t border-white/10"></div>
            <span className="absolute bg-[#090a10] px-3 text-[10px] font-bold uppercase tracking-wider text-gray-500">
              O CON CREDENCIALES
            </span>
          </div>

          {/* Formulario */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                {errorMsg}
              </div>
            )}

            {/* Correo o @usuario */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <label className="text-gray-300 font-medium">Correo electrónico o @usuario</label>
                <span className="text-[10px] text-cyan-400 font-semibold flex items-center gap-1">
                  Verificado
                </span>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                  <AtSign className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ej: valeria_creatrix o valeria@follow.io"
                  className="w-full bg-[#151624] border border-white/10 rounded-xl pl-10 pr-4 py-3 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50 focus:ring-1 focus:ring-pink-500/50"
                  required
                />
              </div>
            </div>

            {/* Contraseña */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <label className="text-gray-300 font-medium">Contraseña</label>
                <button type="button" className="text-[10px] text-gray-400 hover:text-pink-400 transition-colors">
                  ¿Olvidaste tu contraseña?
                </button>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Tu contrasena"
                  className="w-full bg-[#151624] border border-white/10 rounded-xl pl-10 pr-10 py-3 text-base sm:text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50 focus:ring-1 focus:ring-pink-500/50 tracking-wider"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Checkbox y Seguro 256-bit */}
            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-gray-300">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded bg-[#151624] border-white/20 text-pink-600 focus:ring-0 focus:ring-offset-0"
                />
                <span className="text-[11px]">Recordar sesión en este dispositivo</span>
              </label>

              <div className="flex items-center gap-1 text-[10px] text-cyan-400 font-mono">
                <Shield className="w-3.5 h-3.5" />
                <span>Seguro 256-bit</span>
              </div>
            </div>

            {/* Botón CTA Iniciar Sesión en Follow */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-rose-400 text-white font-bold text-xs shadow-xl shadow-pink-500/25 hover:brightness-110 active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{loading ? 'Validando credenciales...' : 'Iniciar Sesión en Follow'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Footer de Registro */}
          <div className="text-center space-y-3 pt-2">
            <p className="text-xs text-gray-400">
              ¿No tienes cuenta?{' '}
              <button
                onClick={() => setMode('register')}
                className="text-pink-400 font-bold hover:underline"
              >
                Regístrate gratis
              </button>
            </p>

            <p className="text-[10px] text-gray-500 leading-relaxed px-4">
              Al continuar aceptas nuestros Términos de Servicio de Streaming y Política de Privacidad de Creador.
            </p>
          </div>

        </div>

      </div>

      {/* FOOTER VACÍO PARA ALINEACIÓN */}
      <div className="py-2"></div>

    </div>
  );
};
