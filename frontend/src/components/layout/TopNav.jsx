import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext.jsx';

export function TopNav({ onOpenMenu, title, subtitle }) {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-slate-950/55 px-4 py-4 backdrop-blur-xl sm:px-8">
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onOpenMenu}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-100 shadow-sm lg:hidden"
            aria-label="Open navigation"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
            </svg>
          </button>
          <div className="min-w-0">
            <motion.h1 layout className="truncate font-display text-lg font-semibold text-white sm:text-xl">
              {title}
            </motion.h1>
            {subtitle ? <p className="truncate text-sm text-slate-400">{subtitle}</p> : null}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-white">
              {user?.firstName} {user?.lastName}
            </p>
            <p className="text-xs capitalize text-violet-200/90">{user?.role}</p>
          </div>
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-violet-400 to-sky-400 p-[2px] shadow-glow">
            <div className="flex h-full w-full items-center justify-center rounded-full bg-slate-950 text-sm font-semibold text-white">
              {(user?.firstName?.[0] || '?').toUpperCase()}
            </div>
          </div>
          <button
            type="button"
            onClick={logout}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:bg-white/10 sm:text-sm"
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
