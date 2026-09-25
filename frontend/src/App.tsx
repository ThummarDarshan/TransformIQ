import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { AppLayout } from './components/layout/AppLayout';

import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { DashboardPage } from './pages/DashboardPage';

import { ProjectsPage } from './pages/ProjectsPage';
import { DiscoveryPage } from './pages/DiscoveryPage';
import { BusinessAnalysisPage } from './pages/BusinessAnalysisPage';
import { GapAnalysisPage } from './pages/GapAnalysisPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { ProcessPage } from './pages/ProcessPage';
import { DatabasePage } from './pages/DatabasePage';
import { ApisPage } from './pages/ApisPage';
import { UxPage } from './pages/UxPage';
import { PlanningPage } from './pages/PlanningPage';
import { SimulationPage } from './pages/SimulationPage';
import { ScorePage } from './pages/ScorePage';
import { BlueprintPage } from './pages/BlueprintPage';
import { CollaborationPage } from './pages/CollaborationPage';
import { AdminPage } from './pages/AdminPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />

              {/* Main Application Layout (Protected) */}
              <Route
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/projects" element={<ProjectsPage />} />

                {/* 13 Pipeline Stages for Project */}
                <Route path="/projects/:id/discovery" element={<DiscoveryPage />} />
                <Route path="/projects/:id/business-analysis" element={<BusinessAnalysisPage />} />
                <Route path="/projects/:id/gap-analysis" element={<GapAnalysisPage />} />
                <Route path="/projects/:id/recommendations" element={<RecommendationsPage />} />
                <Route path="/projects/:id/architecture" element={<ArchitecturePage />} />
                <Route path="/projects/:id/process" element={<ProcessPage />} />
                <Route path="/projects/:id/database" element={<DatabasePage />} />
                <Route path="/projects/:id/apis" element={<ApisPage />} />
                <Route path="/projects/:id/ux" element={<UxPage />} />
                <Route path="/projects/:id/planning" element={<PlanningPage />} />
                <Route path="/projects/:id/simulation" element={<SimulationPage />} />
                <Route path="/projects/:id/score" element={<ScorePage />} />
                <Route path="/projects/:id/blueprint" element={<BlueprintPage />} />

                {/* Governance & Admin */}
                <Route path="/projects/:id/collaboration" element={<CollaborationPage />} />
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute allowedRoles={['ADMIN']}>
                      <AdminPage />
                    </ProtectedRoute>
                  }
                />
              </Route>

              {/* Fallback to Landing Page */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>

        </AuthProvider>
      </LanguageProvider>
    </QueryClientProvider>
  );
};

export default App;
