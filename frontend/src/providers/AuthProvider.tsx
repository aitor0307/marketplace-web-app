import { Center } from '@chakra-ui/react';
import { type ReactNode, useEffect } from 'react';
import { Loader } from '@/components/Loader';
import { authApi } from '@/features/auth/api/auth.api';
import { authService } from '@/services/authService';
import { useSessionStore } from '@/store/sessionStore';

type AuthProviderProps = {
  children: ReactNode;
};

/** Restores the session on boot: stored tokens → GET /api/v1/auth/me. */
export function AuthProvider({ children }: AuthProviderProps) {
  const isHydrated = useSessionStore((s) => s.isHydrated);
  const setHydrated = useSessionStore((s) => s.setHydrated);
  const setUser = useSessionStore((s) => s.setUser);
  const clearSession = useSessionStore((s) => s.clearSession);

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      try {
        if (!authService.hasSession()) {
          clearSession();
          return;
        }
        const user = await authApi.me();
        if (!cancelled) setUser(user);
      } catch {
        authService.clearTokens();
        if (!cancelled) clearSession();
      } finally {
        if (!cancelled) setHydrated(true);
      }
    }

    void hydrate();
    return () => {
      cancelled = true;
    };
  }, [clearSession, setHydrated, setUser]);

  if (!isHydrated) {
    return (
      <Center minH="100vh" bg="brand.pageBg">
        <Loader size="lg" />
      </Center>
    );
  }

  return children;
}
