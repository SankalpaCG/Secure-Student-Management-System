import axios from 'axios';

// Prefer an absolute API origin in dev so CSRF cookies issued by Express are visible to Axios (see README).
const baseURL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:4000' : '');

export const api = axios.create({
  baseURL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
});

function readXsrfCookie() {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.split('; ').find((row) => row.startsWith('XSRF-TOKEN='));
  if (!match) return null;
  return decodeURIComponent(match.split('=').slice(1).join('='));
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ssms_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const xsrf = readXsrfCookie();
  if (xsrf) {
    config.headers['X-XSRF-TOKEN'] = xsrf;
  }
  return config;
});

export async function ensureCsrfCookie() {
  await api.get('/api/v1/auth/csrf');
}
