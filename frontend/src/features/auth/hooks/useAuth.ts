import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect } from 'react';
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

const approvalKey = (token: string) => ['auth', 'approval', token] as const;

export function useApproval(token: string) {
  return useQuery({
    queryKey: approvalKey(token),
    queryFn: () => authApi.getApproval(token),
    enabled: Boolean(token),
    retry: false,
  });
}

export function useApproveUser(token: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => authApi.approve(token),
    onSuccess: (user) => queryClient.setQueryData(approvalKey(token), user),
  });
}

/**
 * Re-reads the signed-in user while they are pending, so an approval that
 * lands while the app is open unlocks publishing without a reload.
 */
export function useRefreshPendingUser() {
  const user = useSessionStore((s) => s.user);
  const setUser = useSessionStore((s) => s.setUser);
  const isPending = user?.status === 'pending';
  const { data } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => authApi.me(),
    enabled: isPending,
    staleTime: 0,
  });
  useEffect(() => {
    if (data) setUser(data);
  }, [data, setUser]);
  return isPending;
}
