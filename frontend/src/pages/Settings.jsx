import { useState } from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from '../components/GlassCard.jsx';
import { api, ensureCsrfCookie } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function Settings() {
  const { refreshProfile } = useAuth();
  const [qr, setQr] = useState('');
  const [code, setCode] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function setup() {
    setError('');
    setMessage('');
    setBusy(true);
    try {
      await ensureCsrfCookie();
      const { data } = await api.post('/api/v1/auth/2fa/setup');
      setQr(data.qrDataUrl);
      setMessage(data.message);
    } catch (e) {
      setError(e.response?.data?.error || 'Unable to start setup');
    } finally {
      setBusy(false);
    }
  }

  async function enable() {
    setError('');
    setMessage('');
    setBusy(true);
    try {
      await ensureCsrfCookie();
      await api.post('/api/v1/auth/2fa/enable', { code });
      setMessage('Two-factor authentication is now enabled.');
      setQr('');
      setCode('');
      await refreshProfile();
    } catch (e) {
      setError(e.response?.data?.error || 'Unable to enable');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-semibold text-white">Security desk</h2>
        <p className="text-sm text-slate-400">TOTP enrollment uses speakeasy-compatible authenticators (Google Authenticator, 1Password, etc.).</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="h-full">
            <h3 className="font-semibold text-white">Authenticator</h3>
            <p className="mt-2 text-sm text-slate-400">Generate a QR, scan it, then confirm with a live code.</p>

            <div className="mt-5 flex flex-wrap gap-3">
              <button
                type="button"
                disabled={busy}
                onClick={setup}
                className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-glow disabled:opacity-60"
              >
                {busy ? 'Working…' : 'Generate QR'}
              </button>
            </div>

            {qr ? (
              <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
                <img src={qr} alt="TOTP QR" className="mx-auto h-48 w-48 rounded-xl bg-white p-2" />
              </div>
            ) : null}

            <label className="mt-6 block text-sm text-slate-300">
              Confirmation code
              <input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none ring-violet-500/40 focus:ring-2"
              />
            </label>

            <button
              type="button"
              disabled={busy || !code}
              onClick={enable}
              className="mt-4 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10 disabled:opacity-50"
            >
              Enable 2FA
            </button>

            {message ? <p className="mt-4 text-sm text-emerald-300">{message}</p> : null}
            {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
          </GlassCard>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <GlassCard className="h-full glass-strong">
            <h3 className="font-semibold text-white">Defense-in-depth</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">Helmet + strict CORS for browser clients.</li>
              <li className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">Double-submit CSRF on mutating verbs.</li>
              <li className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">Rate limits tuned for auth endpoints.</li>
              <li className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">Input validation and HTML-safe string handling.</li>
            </ul>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}
