/**
 * Enrutador Principal de la Aplicacion Follow.
 * Arquitectura SPA con React Router v6 y cobertura de todas las secciones.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { Navbar } from './components/layout/Navbar';
import { BottomNav } from './components/layout/BottomNav';
import { FeedPage } from './pages/FeedPage';
import { ExplorePage } from './pages/ExplorePage';
import { TrendsPage } from './pages/TrendsPage';
import { LivePage } from './pages/LivePage';
import { ActivityPage } from './pages/ActivityPage';
import { ProfilePage } from './pages/ProfilePage';
import { StudioPage } from './pages/StudioPage';
import { AuthPage } from './pages/AuthPage';

const AppContent: React.FC = () => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/registro';

  return (
    <div className="min-h-screen min-h-[100dvh] bg-[#0c0d14] text-white flex flex-col justify-between selection:bg-pink-500 selection:text-white overflow-x-hidden">
      {!isAuthPage && <Navbar />}

      <main className="flex-1 w-full">
        <Routes>
          <Route path="/" element={<FeedPage />} />
          <Route path="/explorar" element={<ExplorePage />} />
          <Route path="/tendencias" element={<TrendsPage />} />
          <Route path="/en-vivo" element={<LivePage />} />
          <Route path="/actividad" element={<ActivityPage />} />
          <Route path="/perfil" element={<ProfilePage />} />
          <Route path="/estudio" element={<StudioPage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/registro" element={<AuthPage />} />
        </Routes>
      </main>

      {!isAuthPage && <BottomNav />}
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
