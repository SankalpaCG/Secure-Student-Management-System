import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from '../components/GlassCard.jsx';
import { api, ensureCsrfCookie } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function Courses() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function refresh() {
    const { data } = await api.get('/api/v1/courses');
    setCourses(data.courses || []);
  }

  useEffect(() => {
    refresh().catch((e) => setError(e.response?.data?.error || 'Unable to load courses'));
  }, []);

  async function enroll(courseId) {
    setMessage('');
    setError('');
    try {
      await ensureCsrfCookie();
      await api.post(`/api/v1/courses/${courseId}/enroll`);
      setMessage('Enrollment updated.');
      await refresh();
    } catch (e) {
      setError(e.response?.data?.error || 'Unable to enroll');
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-semibold text-white">Courses</h2>
        <p className="text-sm text-slate-400">Glass table layout with responsive overflow and motion accents.</p>
      </div>

      {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-300">{message}</p> : null}

      <GlassCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0 text-sm">
            <thead>
              <tr className="bg-white/5 text-left text-xs uppercase tracking-wider text-slate-400">
                <th className="px-6 py-4">Code</th>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Credits</th>
                <th className="px-6 py-4">Teacher</th>
                {user?.role === 'student' ? <th className="px-6 py-4">Action</th> : null}
              </tr>
            </thead>
            <tbody>
              {courses.map((c, idx) => (
                <motion.tr
                  key={c.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="border-t border-white/10 hover:bg-white/[0.03]"
                >
                  <td className="px-6 py-4 font-semibold text-violet-100">{c.code}</td>
                  <td className="px-6 py-4 text-slate-100">{c.name}</td>
                  <td className="px-6 py-4 text-slate-300">{c.credits}</td>
                  <td className="px-6 py-4 text-slate-300">
                    {c.teacher ? `${c.teacher.firstName} ${c.teacher.lastName}` : '—'}
                  </td>
                  {user?.role === 'student' ? (
                    <td className="px-6 py-4">
                      <button
                        type="button"
                        onClick={() => enroll(c.id)}
                        className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white hover:bg-white/10"
                      >
                        Enroll
                      </button>
                    </td>
                  ) : null}
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
