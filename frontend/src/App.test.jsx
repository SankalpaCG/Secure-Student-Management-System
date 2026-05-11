import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import App from './App.jsx';

vi.mock('./api/client.js', () => {
  const api = {
    get: vi.fn(() => Promise.reject(new Error('unauthenticated'))),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() } }
  };
  return { api, ensureCsrfCookie: vi.fn(() => Promise.resolve()) };
});

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders login route', async () => {
    const { api } = await import('./api/client.js');
    api.get.mockImplementation((url) => {
      if (url === '/api/v1/auth/me') {
        return Promise.reject({ response: { status: 401 } });
      }
      return Promise.reject(new Error('unexpected'));
    });

    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByText(/Welcome back/i)).toBeInTheDocument();
  });
});
