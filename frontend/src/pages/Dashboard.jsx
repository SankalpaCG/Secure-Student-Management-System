import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { GlassCard } from '../components/GlassCard.jsx';
import { api } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

function Stat({ label, value, hint }) {
  return (
    <GlassCard className="relative overflow-hidden">
      <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-violet-500/15 blur-2xl" />
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-3 font-display text-3xl font-semibold text-white">{value}</p>
      {hint ? <p className="mt-2 text-xs text-slate-400">{hint}</p> : null}
    </GlassCard>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [activity, setActivity] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [s, a] = await Promise.all([
          api.get('/api/v1/dashboard/summary'),
          api.get('/api/v1/dashboard/activity').catch(() => ({ data: { enrollmentsByMonth: [] } }))
        ]);
        if (!cancelled) {
          setSummary(s.data);
          setActivity(a.data.enrollmentsByMonth || []);
        }
      } catch (e) {
        if (!cancelled) setError(e.response?.data?.error || 'Unable to load dashboard');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const chartData = useMemo(
    () =>
      (activity || []).map((row) => ({
        month: row.month,
        count: Number(row.count)
      })),
    [activity]
  );

  const adminStats = useMemo(() => {
    if (!summary || summary.scope !== 'admin') return null;
    const u = summary.usersByRole || {};
    return [
      { label: 'Admins', value: u.admin || 0, hint: 'Platform operators' },
      { label: 'Teachers', value: u.teacher || 0, hint: 'Instructional staff' },
      { label: 'Students', value: u.student || 0, hint: 'Active learner accounts' },
      { label: 'Courses', value: summary.courses || 0, hint: 'Published catalog items' },
      { label: 'Enrollments', value: summary.enrollments || 0, hint: 'Seat-moments across terms' }
    ];
  }, [summary]);

  const teacherStats = useMemo(() => {
    if (!summary || summary.scope !== 'teacher') return null;
    return [
      { label: 'Teaching', value: summary.teachingCourses || 0, hint: 'Courses you own' },
      { label: 'Roster reach', value: summary.studentsTaught || 0, hint: 'Distinct students taught' }
    ];
  }, [summary]);

  const studentStats = useMemo(() => {
    if (!summary || summary.scope !== 'student') return null;
    return [
      { label: 'Active seats', value: summary.activeEnrollments || 0, hint: 'Currently enrolled' },
      { label: 'Completed', value: summary.completedCourses || 0, hint: 'Finished pathways' }
    ];
  }, [summary]);

  const stats = adminStats || teacherStats || studentStats || [];

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-violet-200/90">Signed in as</p>
          <h2 className="font-display text-2xl font-semibold text-white sm:text-3xl">
            {user?.firstName} {user?.lastName}
          </h2>
          <p className="text-sm text-slate-400">Role: {user?.role}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200 backdrop-blur-xl">
          <span className="font-semibold text-white">Tip:</span> enable TOTP under Security to harden high-privilege sessions.
        </div>
      </motion.div>

      {error ? <p className="text-sm text-rose-300">{error}</p> : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {stats.map((s, idx) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
            <Stat {...s} />
          </motion.div>
        ))}
      </div>

      <GlassCard className="glass-strong">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-display text-lg font-semibold text-white">Enrollment cadence</h3>
            <p className="text-sm text-slate-400">Trailing months (admin / teacher visibility).</p>
          </div>
          <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">Recharts</div>
        </div>

        <div className="mt-6 h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData.length ? chartData : [{ month: '—', count: 0 }]}>
              <defs>
                <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.55} />
                  <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
              <XAxis dataKey="month" stroke="rgba(148,163,184,0.55)" tick={{ fill: 'rgba(226,232,240,0.65)', fontSize: 12 }} />
              <YAxis stroke="rgba(148,163,184,0.55)" tick={{ fill: 'rgba(226,232,240,0.65)', fontSize: 12 }} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(2,6,23,0.85)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 12
                }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Area type="monotone" dataKey="count" stroke="#c4b5fd" strokeWidth={2} fill="url(#fill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>
    </div>
  );
}
