import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwt_decode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp > currentTime) {
          // Set auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Get user data
          fetchUserData();
        } else {
          // Token expired
          logout();
        }
      } catch (error) {
        console.error('Invalid token', error);
        logout();
      }
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/users/me/`);
      setCurrentUser(response.data);
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user data', error);
      logout();
    }
  };

  const login = async (email, password) => {
    try {
      setError('');
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/token`, formData);
      
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // Set auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user data
      await fetchUserData();
      
      return true;
    } catch (error) {
      console.error('Login error', error);
      setError(error.response?.data?.detail || 'Une erreur est survenue lors de la connexion');
      return false;
    }
  };

  const register = async (email, password, fullName) => {
    try {
      setError('');
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/users/`, {
        email,
        password,
        full_name: fullName
      });
      
      // Auto login after registration
      return await login(email, password);
    } catch (error) {
      console.error('Registration error', error);
      setError(error.response?.data?.detail || 'Une erreur est survenue lors de l\'inscription');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setCurrentUser(null);
    setIsAuthenticated(false);
    setLoading(false);
  };

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
