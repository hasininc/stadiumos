import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface Role {
  name: string;
  description?: string;
}

interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  roles: Role[];
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshTokens: () => Promise<string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post('/api/v1/auth/login', { email, password });
      setAccessToken(response.data.access_token);
      
      const userResponse = await axios.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${response.data.access_token}` }
      });
      setUser(userResponse.data);
    } catch (error) {
      logout();
      throw error;
    }
  };

  const logout = async () => {
    try {
      const oldRefreshToken = localStorage.getItem('stadiumos_refresh_token');
      if (oldRefreshToken) {
        await axios.post('/api/v1/auth/logout', { refresh_token: oldRefreshToken });
      }
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('stadiumos_refresh_token');
      setAccessToken(null);
      setUser(null);
    }
  };

  const refreshTokens = async (): Promise<string> => {
    const localRefreshToken = localStorage.getItem('stadiumos_refresh_token');
    if (!localRefreshToken) throw new Error('No refresh token exists');
    
    const response = await axios.post('/api/v1/auth/refresh', { refresh_token: localRefreshToken });
    setAccessToken(response.data.access_token);
    return response.data.access_token;
  };

  useEffect(() => {
    const bootstrapAuth = async () => {
      try {
        const token = await refreshTokens();
        const userResponse = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(userResponse.data);
      } catch (e) {
        logout();
      } finally {
        setLoading(false);
      }
    };
    bootstrapAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, login, logout, refreshTokens }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be executed within an AuthProvider');
  return context;
};
