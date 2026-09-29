import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { authApi } from '@/features/auth/api/auth.api';
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/features/auth/types/auth.types';
import { analyticsService } from '@/services/analyticsService';
import { authService } from '@/services/authService';
import { useSessionStore } from '@/store/sessionStore';

function persistAuth(data: AuthResponse) {
  authService.setTokens(data.access_token, data.refresh_token);
  useSessionStore.getState().setUser(data.user);
  analyticsService.identify(String(data.user.id), { email: data.user.email });
}

export function useLogin() {
  return useMutation({
    mutationFn: (payload: LoginRequest) => authApi.login(payload),
    onSuccess: (data) => {
      persistAuth(data);
      analyticsService.track('login_success');
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (payload: RegisterRequest) => authApi.register(payload),
    onSuccess: (data) => {
      persistAuth(data);
      analyticsService.track('register_success');
    },
  });
}

/** JWTs are stateless server-side, so logging out is purely local. */
export function useLogout() {
  const queryClient = useQueryClient();
  const clearSession = useSessionStore((s) => s.clearSession);

  return useCallback(() => {
    authService.clearTokens();
    clearSession();
    queryClient.clear();
    analyticsService.track('logout');
  }, [clearSession, queryClient]);
}
