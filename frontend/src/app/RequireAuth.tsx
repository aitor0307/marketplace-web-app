import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { ROUTES } from '@/config/constants';
import { useSessionStore } from '@/store/sessionStore';

/** Replaces flask-login's @login_required: bounce to /login and come back after. */
export function RequireAuth() {
  const isAuthenticated = useSessionStore((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.login} replace state={{ from: location }} />;
  }

  return <Outlet />;
}

/** Login/register are pointless once signed in (the views redirected to the index too). */
export function RequireGuest() {
  const isAuthenticated = useSessionStore((s) => s.isAuthenticated);
  return isAuthenticated ? <Navigate to={ROUTES.home} replace /> : <Outlet />;
}
