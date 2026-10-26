/**
 * Modal de Mensajes Directos (Follow Direct Messages).
 * Panel interactivo para conversar con creadores y colaboradores.
 */

import React, { useState } from 'react';
import { 
  Send, X, Search, CheckCircle, Circle, ArrowLeft 
} from 'lucide-react';

interface DirectChat {
  id: string;
  user: string;
  name: string;
  avatar: string;
  lastMessage: string;
  time: string;
  unreadCount: number;
  isOnline: boolean;
  messages: { sender: 'me' | 'them'; text: string; time: string }[];
}

interface DirectMessagesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DirectMessagesModal: React.FC<DirectMessagesModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const [chats, setChats] = useState<DirectChat[]>([
    {
      id: '1',
      user: 'sofia.k',
      name: 'Sofia K',
      avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100',
      lastMessage: 'Viste la transmision en vivo de anoche? Salio increible!',
      time: '16:15',
      unreadCount: 2,
      isOnline: true,
      messages: [
        { sender: 'them', text: 'Hola Valeria! Como va ese nuevo setup?', time: '16:10' },
        { sender: 'me', text: 'Quedo brutal! Ya lo publique en Follow.', time: '16:12' },
        { sender: 'them', text: 'Viste la transmision en vivo de anoche? Salio increible!', time: '16:15' }
      ]
    },
    {
      id: '2',
      user: 'mateo_vfx',
      name: 'Mateo VFX',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100',
      lastMessage: 'Te acabo de enviar los LUTs de DaVinci por correo.',
      time: '14:20',
      unreadCount: 0,
      isOnline: false,
      messages: [
        { sender: 'them', text: 'Te acabo de enviar los LUTs de DaVinci por correo.', time: '14:20' }
      ]
    },
    {
      id: '3',
      user: 'kira_techwear',
      name: 'Kira Vex',
      avatar: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=100',
      lastMessage: 'Cuando coordinamos el rodaje en Shibuya?',
      time: 'Ayer',
      unreadCount: 0,
      isOnline: true,
      messages: [
        { sender: 'them', text: 'Cuando coordinamos el rodaje en Shibuya?', time: 'Ayer' }
      ]
    }
  ]);

  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');

  const currentChat = chats.find(c => c.id === activeChatId);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !activeChatId) return;

    setChats(prev => prev.map(chat => {
      if (chat.id === activeChatId) {
        return {
          ...chat,
          lastMessage: inputText.trim(),
          time: 'Ahora',
          messages: [
            ...chat.messages,
            { sender: 'me', text: inputText.trim(), time: 'Ahora' }
          ]
        };
      }
      return chat;
    }));

    setInputText('');
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl h-[560px] rounded-3xl bg-[#131422] border border-white/10 shadow-2xl flex overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* LISTA DE CONVERSACIONES (PANEL IZQUIERDO) */}
        <div className={`w-full sm:w-72 border-r border-white/10 flex flex-col justify-between ${
          activeChatId ? 'hidden sm:flex' : 'flex'
        }`}>
          <div>
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-sm font-bold text-white">Mensajes Directos</h2>
              <button onClick={onClose} className="sm:hidden text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-gray-400 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Buscar chat..."
                  className="w-full bg-[#1b1c2e] border border-white/5 rounded-xl pl-8 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="overflow-y-auto max-h-[420px] px-2 space-y-1">
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  onClick={() => setActiveChatId(chat.id)}
                  className={`p-2.5 rounded-2xl flex items-center gap-3 cursor-pointer transition-colors ${
                    activeChatId === chat.id
                      ? 'bg-white/10'
                      : 'hover:bg-white/5'
                  }`}
                >
                  <div className="relative flex-shrink-0">
                    <img src={chat.avatar} alt="" className="w-10 h-10 rounded-full object-cover" />
                    {chat.isOnline && (
                      <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 border border-[#131422]"></span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white truncate">{chat.name}</span>
                      <span className="text-[10px] text-gray-500">{chat.time}</span>
                    </div>
                    <p className="text-[11px] text-gray-400 truncate mt-0.5">{chat.lastMessage}</p>
                  </div>
                  {chat.unreadCount > 0 && (
                    <span className="w-4 h-4 rounded-full bg-pink-600 text-white text-[9px] font-bold flex items-center justify-center flex-shrink-0">
                      {chat.unreadCount}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AREA DE CONVERSACION (PANEL DERECHO) */}
        <div className={`flex-1 flex flex-col justify-between bg-[#0e0f19] ${
          !activeChatId ? 'hidden sm:flex items-center justify-center' : 'flex'
        }`}>
          {currentChat ? (
            <>
              {/* Cabecera del chat activo */}
              <div className="p-3.5 border-b border-white/10 flex items-center justify-between bg-[#131422]">
                <div className="flex items-center gap-2.5">
                  <button
                    onClick={() => setActiveChatId(null)}
                    className="sm:hidden p-1 text-gray-400 hover:text-white mr-1"
                  >
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                  <img src={currentChat.avatar} alt="" className="w-8 h-8 rounded-full object-cover" />
                  <div>
                    <span className="text-xs font-bold text-white block">{currentChat.name}</span>
                    <span className="text-[10px] text-cyan-400 block -mt-0.5">@{currentChat.user}</span>
                  </div>
                </div>
                <button onClick={onClose} className="text-gray-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Mensajes */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {currentChat.messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex flex-col ${m.sender === 'me' ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[75%] px-3.5 py-2 rounded-2xl text-xs leading-relaxed ${
                        m.sender === 'me'
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none'
                          : 'bg-[#1c1d2e] text-gray-200 rounded-bl-none border border-white/5'
                      }`}
                    >
                      {m.text}
                    </div>
                    <span className="text-[9px] text-gray-500 mt-1 px-1">{m.time}</span>
                  </div>
                ))}
              </div>

              {/* Input para enviar mensaje */}
              <form onSubmit={handleSendMessage} className="p-3 border-t border-white/10 bg-[#131422] flex items-center gap-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={`Escribe un mensaje para ${currentChat.name}...`}
                  className="flex-1 bg-[#1c1d2e] border border-white/10 rounded-2xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pink-500/50"
                />
                <button
                  type="submit"
                  disabled={!inputText.trim()}
                  className="p-2.5 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 text-white disabled:opacity-40"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </>
          ) : (
            <div className="text-center text-gray-500 p-8 space-y-2">
              <Send className="w-8 h-8 mx-auto opacity-30" />
              <p className="text-xs">Selecciona una conversacion para comenzar a chatear.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
