import { create } from 'zustand';
import type { User } from '@/types/models';

type SessionState = {
  user: User | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  setUser: (user: User | null) => void;
  setHydrated: (hydrated: boolean) => void;
  clearSession: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  user: null,
  isAuthenticated: false,
  isHydrated: false,
  setUser: (user) => set({ user, isAuthenticated: Boolean(user) }),
  setHydrated: (isHydrated) => set({ isHydrated }),
  clearSession: () => set({ user: null, isAuthenticated: false }),
}));
