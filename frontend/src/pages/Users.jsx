import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GlassCard } from '../components/GlassCard.jsx';
import { api } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function Users() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.role !== 'admin') return;
    api
      .get('/api/v1/users')
      .then((res) => setUsers(res.data.users || []))
      .catch((e) => setError(e.response?.data?.error || 'Unable to load users'));
  }, [user?.role]);

  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-semibold text-white">Directory</h2>
        <p className="text-sm text-slate-400">Administrative roster with role chips and soft metadata.</p>
      </div>

      {error ? <p className="text-sm text-rose-300">{error}</p> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {users.map((u, idx) => (
          <motion.div key={u.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}>
            <GlassCard className="h-full">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-white">
                    {u.firstName} {u.lastName}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">{u.email}</p>
                </div>
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold capitalize text-violet-100 ring-1 ring-white/10">
                  {u.role}
                </span>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-400">
                <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                  <p className="font-semibold text-slate-200">Department</p>
                  <p className="mt-1 text-slate-300">{u.department || '—'}</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                  <p className="font-semibold text-slate-200">Student ID</p>
                  <p className="mt-1 text-slate-300">{u.studentId || '—'}</p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
