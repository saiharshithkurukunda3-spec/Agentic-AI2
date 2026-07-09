import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Profile from './pages/Profile';
import Research from './pages/Research';
import History from './pages/History';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-[#0a0a0f] text-slate-100 selection:bg-indigo-500/30 selection:text-indigo-200">
          
          {/* Main Navigation Header */}
          <Navbar />
          
          {/* Core Route Wrapper */}
          <main className="flex-grow container mx-auto px-4 py-8">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* Protected Routes */}
              <Route
                path="/research"
                element={
                  <ProtectedRoute>
                    <Research />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <History />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />

              {/* Catch All Redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          {/* Subtle footer */}
          <footer className="py-6 border-t border-brand-border bg-[#07070b]/60 text-center text-xs text-slate-600">
            &copy; {new Date().getFullYear()} VERITAS AI. Built for premium RAG performance.
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
