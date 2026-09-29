import type { User } from '@/types/models';

export type LoginRequest = {
  email: string;
  password: string;
};

/** Mirrors RegisterPayload in app/schemas/auth.py. */
export type RegisterRequest = {
  name: string;
  email: string;
  password: string;
  state: string;
  city: string;
};

/** Mirrors AuthResponse in app/schemas/common.py. */
export type AuthResponse = {
  user: User;
  access_token: string;
  refresh_token: string;
};
