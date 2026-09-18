import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/users/profile');
      setUser(response.data);
      return response.data;
    } catch (err) {
      localStorage.removeItem('token');
      setUser(null);
      throw err;
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile()
        .catch(() => {
          localStorage.removeItem('token');
          setUser(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    const token = response.data.access_token;
    localStorage.setItem('token', token);
    
    const profileResponse = await api.get('/users/profile', {
      headers: { Authorization: `Bearer ${token}` }
    });
    setUser(profileResponse.data);
    return profileResponse.data;
  };

  const register = async (userData) => {
    await api.post('/auth/register', userData);
    await login(userData.email, userData.password);
  };

  const updateUser = (updatedData) => {
    setUser(prevUser => (prevUser ? { ...prevUser, ...updatedData } : updatedData));
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, updateUser, fetchUserProfile, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
