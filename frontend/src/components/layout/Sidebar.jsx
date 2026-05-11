import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';

const links = [
  { to: '/', label: 'Overview', end: true, roles: ['admin', 'teacher', 'student'] },
  { to: '/courses', label: 'Courses', roles: ['admin', 'teacher', 'student'] },
  { to: '/users', label: 'Directory', roles: ['admin'] },
  { to: '/settings', label: 'Security', roles: ['admin', 'teacher', 'student'] }
];

function IconGrid() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 4h6v6H4V4Zm10 0h6v6h-6V4ZM4 14h6v6H4v-6Zm10 0h6v6h-6v-6Z" />
    </svg>
  );
}

export function Sidebar({ role, onNavigate }) {
  const visible = links.filter((l) => l.roles.includes(role));

  return (
    <aside className="flex h-full flex-col border-r border-white/10 bg-slate-950/40 px-4 py-6 backdrop-blur-xl">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-glow">
          <IconGrid />
        </div>
        <div>
          <p className="font-display text-sm font-semibold tracking-wide text-white">SSMS</p>
          <p className="text-xs text-slate-400">Secure campus ops</p>
        </div>
      </div>

      <nav className="scrollbar-thin flex flex-1 flex-col gap-1 overflow-y-auto">
        {visible.map((item, idx) => (
          <motion.div key={item.to} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.04 }}>
            <NavLink
              to={item.to}
              end={item.end}
              onClick={() => onNavigate?.()}
              className={({ isActive }) =>
                [
                  'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all',
                  isActive
                    ? 'bg-white/10 text-white shadow-inner ring-1 ring-white/15'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                ].join(' ')
              }
            >
              <span className="h-1.5 w-1.5 rounded-full bg-gradient-to-r from-violet-400 to-sky-400 opacity-70 group-hover:opacity-100" />
              {item.label}
            </NavLink>
          </motion.div>
        ))}
      </nav>

      <div className="mt-6 rounded-xl border border-white/10 bg-gradient-to-br from-violet-500/15 to-sky-500/10 p-4 text-xs text-slate-200">
        <p className="font-semibold text-white">Zero-trust posture</p>
        <p className="mt-1 leading-relaxed text-slate-300">JWT sessions, RBAC, TOTP-ready accounts, and hardened API defaults.</p>
      </div>
    </aside>
  );
}
