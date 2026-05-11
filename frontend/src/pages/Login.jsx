import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import { GlassCard } from '../components/GlassCard.jsx';

export default function Login() {
  const { user, loading, login, completeTwoFactor } = useAuth();
  const [email, setEmail] = useState('admin@ssms.local');
  const [password, setPassword] = useState('ChangeMe!1');
  const [code, setCode] = useState('');
  const [tempToken, setTempToken] = useState(null);
  const [previewUser, setPreviewUser] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const result = await login(email, password);
      if (result.requiresTwoFactor) {
        setTempToken(result.tempToken);
        setPreviewUser(result.previewUser);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to sign in');
    } finally {
      setBusy(false);
    }
  }

  async function onVerify2fa(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await completeTwoFactor(tempToken, code);
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid code');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute -left-32 top-0 h-[520px] w-[520px] rounded-full bg-violet-600/25 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 bottom-0 h-[520px] w-[520px] rounded-full bg-sky-500/20 blur-3xl" />

      <div className="relative z-10 mx-auto grid min-h-screen max-w-6xl items-center gap-10 px-4 py-10 lg:grid-cols-2 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }} className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-violet-100">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            Live security posture
          </div>
          <h1 className="font-display text-4xl font-semibold leading-tight text-white sm:text-5xl">
            Secure Student Management, <span className="text-transparent bg-gradient-to-r from-violet-200 to-sky-200 bg-clip-text">designed for trust.</span>
          </h1>
          <p className="max-w-xl text-base leading-relaxed text-slate-300 sm:text-lg">
            Role-aware workspaces, hardened APIs, and modern authentication flows — including optional TOTP second factors for high-assurance access.
          </p>

          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { k: 'RBAC', v: 'Admin · Teacher · Student' },
              { k: 'API', v: 'Helmet · CORS · CSRF · limits' },
              { k: '2FA', v: 'TOTP enrollment ready' }
            ].map((item) => (
              <div key={item.k} className="glass rounded-2xl p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-violet-200/90">{item.k}</p>
                <p className="mt-2 text-sm text-slate-200">{item.v}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08, duration: 0.45 }}>
          <GlassCard className="glass-strong">
            {!tempToken ? (
              <form onSubmit={onSubmit} className="space-y-5">
                <div>
                  <h2 className="font-display text-2xl font-semibold text-white">Welcome back</h2>
                  <p className="mt-1 text-sm text-slate-400">Use your institutional email to continue.</p>
                </div>

                <label className="block text-sm text-slate-300">
                  Email
                  <input
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    type="email"
                    autoComplete="username"
                    className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none ring-violet-500/40 transition focus:ring-2"
                    required
                  />
                </label>

                <label className="block text-sm text-slate-300">
                  Password
                  <input
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    type="password"
                    autoComplete="current-password"
                    className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none ring-violet-500/40 transition focus:ring-2"
                    required
                  />
                </label>

                {error ? <p className="text-sm text-rose-300">{error}</p> : null}

                <button
                  type="submit"
                  disabled={busy}
                  className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-60"
                >
                  {busy ? 'Signing in…' : 'Continue'}
                </button>
              </form>
            ) : (
              <form onSubmit={onVerify2fa} className="space-y-5">
                <div>
                  <h2 className="font-display text-2xl font-semibold text-white">Two-factor check</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Enter the code from your authenticator for{' '}
                    <span className="font-medium text-white">
                      {previewUser?.firstName} {previewUser?.lastName}
                    </span>
                    .
                  </p>
                </div>

                <label className="block text-sm text-slate-300">
                  6-digit code
                  <input
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    className="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none ring-violet-500/40 transition focus:ring-2"
                    required
                  />
                </label>

                {error ? <p className="text-sm text-rose-300">{error}</p> : null}

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setTempToken(null);
                      setCode('');
                      setError('');
                    }}
                    className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100 hover:bg-white/10"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={busy}
                    className="flex-1 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-60"
                  >
                    {busy ? 'Verifying…' : 'Verify'}
                  </button>
                </div>
              </form>
            )}
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}
