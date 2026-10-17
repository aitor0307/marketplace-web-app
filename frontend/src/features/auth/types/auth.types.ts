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
  /** Without the right key the account is created pending approval. */
  registration_key?: string;
};

/** Mirrors AuthResponse in app/schemas/common.py. */
export type AuthResponse = {
  user: User;
  access_token: string;
  refresh_token: string;
};

/** Mirrors RegisterResponse: who to contact, set only when the account is pending. */
export type RegisterResponse = AuthResponse & {
  contact_email: string | null;
};
