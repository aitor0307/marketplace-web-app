import { apiClient } from '@/services/apiClient';
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/features/auth/types/auth.types';
import type { User } from '@/types/models';

export const authApi = {
  login(payload: LoginRequest): Promise<AuthResponse> {
    return apiClient<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: payload,
      auth: false,
    });
  },

  register(payload: RegisterRequest): Promise<AuthResponse> {
    return apiClient<AuthResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: payload,
      auth: false,
    });
  },

  me(): Promise<User> {
    return apiClient<{ user: User }>('/api/v1/auth/me').then((res) => res.user);
  },

  /** The signed token from the approval email is the only authorization. */
  getApproval(token: string): Promise<User> {
    return apiClient<{ user: User }>(`/api/v1/auth/approvals/${encodeURIComponent(token)}`, {
      auth: false,
    }).then((res) => res.user);
  },

  approve(token: string): Promise<User> {
    return apiClient<{ user: User }>(`/api/v1/auth/approvals/${encodeURIComponent(token)}`, {
      method: 'POST',
      auth: false,
    }).then((res) => res.user);
  },
};
