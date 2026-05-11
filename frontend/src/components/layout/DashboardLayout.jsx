import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './Sidebar.jsx';
import { TopNav } from './TopNav.jsx';
import { useAuth } from '../../context/AuthContext.jsx';

const titles = {
  '/': { title: 'Mission control', subtitle: 'Live signals across students, faculty, and courses.' },
  '/courses': { title: 'Course fabric', subtitle: 'Catalog, teaching assignments, and enrollment health.' },
  '/users': { title: 'People directory', subtitle: 'Administrative visibility with least privilege.' },
  '/settings': { title: 'Security desk', subtitle: 'Authenticator enrollment and session hygiene.' }
};

export function DashboardLayout() {
  const { user } = useAuth();
  const location = useLocation();
  const meta = titles[location.pathname] || titles['/'];
  const [mobileNav, setMobileNav] = useState(false);

  return (
    <div className="relative min-h-screen bg-[length:48px_48px] bg-grid-fade">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-slate-950/40 via-transparent to-slate-950/80" />

      <div className="relative z-10 flex min-h-screen">
        <div className="hidden w-72 shrink-0 lg:block">
          <Sidebar role={user?.role || 'student'} />
        </div>

        <AnimatePresence>
          {mobileNav ? (
            <motion.div
              className="fixed inset-0 z-40 lg:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <button
                type="button"
                className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
                aria-label="Close navigation"
                onClick={() => setMobileNav(false)}
              />
              <motion.aside
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: 'spring', stiffness: 320, damping: 32 }}
                className="absolute left-0 top-0 h-full w-[min(88vw,320px)] border-r border-white/10 bg-slate-950/90 shadow-2xl"
              >
                <Sidebar role={user?.role || 'student'} onNavigate={() => setMobileNav(false)} />
              </motion.aside>
            </motion.div>
          ) : null}
        </AnimatePresence>

        <div className="flex min-w-0 flex-1 flex-col">
          <TopNav title={meta.title} subtitle={meta.subtitle} onOpenMenu={() => setMobileNav(true)} />
          <main className="flex-1 px-4 py-6 sm:px-8 sm:py-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
