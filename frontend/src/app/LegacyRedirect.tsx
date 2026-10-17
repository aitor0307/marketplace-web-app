import { Navigate, useLocation, useParams } from 'react-router-dom';

type LegacyRedirectProps = {
  to: (params: Record<string, string | undefined>) => string;
};

/**
 * Old Jinja URLs (/listing/3, /user/5, ...) keep working once the SPA takes
 * over the domain — bookmarks and links in already-sent emails included.
 */
export function LegacyRedirect({ to }: LegacyRedirectProps) {
  const params = useParams();
  const { search } = useLocation();
  const target = to(params);
  return <Navigate to={target.includes('?') ? target : `${target}${search}`} replace />;
}
