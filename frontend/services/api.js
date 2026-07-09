import axios from 'axios';

// Get API URL from env, default to local FastAPI dev server
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Crucial for receiving and sending HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Optional interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If we receive a 401 and the route isn't /login or /signup,
    // we can handle clearing auth state if necessary
    const currentPath = window.location.pathname;
    if (error.response && error.response.status === 401 && currentPath !== '/login' && currentPath !== '/signup' && currentPath !== '/') {
      // Access token expired or invalid, redirect to login
      logger_dev_info("Unauthorized access detected, forwarding to login page");
      // Let the page handle it via AuthContext state or force redirect
    }
    return Promise.reject(error);
  }
);

function logger_dev_info(msg) {
  if (import.meta.env.DEV) {
    console.log(`[API Interceptor] ${msg}`);
  }
}

export default api;
