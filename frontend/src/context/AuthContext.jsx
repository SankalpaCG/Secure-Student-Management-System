import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api, ensureCsrfCookie } from '../api/client.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('ssms_token'));
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('ssms_token');
    setToken(null);
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get('/api/v1/auth/me');
      setUser(data.user);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  }, [token, logout]);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  const login = useCallback(async (email, password) => {
    await ensureCsrfCookie();
    const { data } = await api.post('/api/v1/auth/login', { email, password });
    if (data.requiresTwoFactor) {
      return { requiresTwoFactor: true, tempToken: data.tempToken, previewUser: data.user };
    }
    localStorage.setItem('ssms_token', data.accessToken);
    setToken(data.accessToken);
    setUser(data.user);
    return { requiresTwoFactor: false };
  }, []);

  const completeTwoFactor = useCallback(async (tempToken, code) => {
    await ensureCsrfCookie();
    const { data } = await api.post('/api/v1/auth/2fa/verify', { tempToken, code });
    localStorage.setItem('ssms_token', data.accessToken);
    setToken(data.accessToken);
    setUser(data.user);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      logout,
      completeTwoFactor,
      refreshProfile
    }),
    [user, token, loading, login, logout, completeTwoFactor, refreshProfile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
