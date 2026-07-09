import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check auth session on startup
  useEffect(() => {
    const initAuth = async () => {
      try {
        const response = await api.get('/auth/profile');
        if (response.data) {
          setUser(response.data);
        }
      } catch (err) {
        // Unauthenticated is expected if cookie is empty
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data && response.data.user) {
        setUser(response.data.user);
        return response.data.user;
      }
    } catch (err) {
      throw err.response?.data?.detail || 'Login failed. Please check credentials.';
    }
  };

  const signup = async (username, email, password) => {
    try {
      await api.post('/auth/signup', { username, email, password });
    } catch (err) {
      throw err.response?.data?.detail || 'Registration failed.';
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (err) {
      console.error('Logout request failed', err);
    } finally {
      // Always clear local state
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    checkSession: async () => {
      try {
        const res = await api.get('/auth/profile');
        setUser(res.data);
      } catch (e) {
        setUser(null);
      }
    }
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
