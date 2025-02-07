import { useState } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import SignIn from './pages/SignIn';
import { useAuth } from './contexts/AuthContext';
import { ModelProvider } from './contexts/ModelContext';
import AddSource from './pages/AddSource';
import PasswordReset from '@/pages/PasswordReset';
import { MainApp } from './components/Main';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/signin" />;
  }

  return <>{children}</>;
};

export default function App() {
  return (
    <AuthProvider>
      <ModelProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <MainApp />
                </PrivateRoute>
              }
            />
            <Route path="/sources/add" element={<AddSource />} />
            <Route path="/password-reset" element={<PasswordReset />} />
          </Routes>
        </BrowserRouter>
      </ModelProvider>
    </AuthProvider>
  );
}
