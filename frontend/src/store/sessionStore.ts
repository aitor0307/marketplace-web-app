import { create } from 'zustand';
import type { User } from '@/types/models';

/** Shown once after signing up without a valid registration code. */
export type PendingApprovalNotice = {
  contactEmail: string | null;
};

type SessionState = {
  user: User | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  pendingApprovalNotice: PendingApprovalNotice | null;
  setUser: (user: User | null) => void;
  setHydrated: (hydrated: boolean) => void;
  showPendingApprovalNotice: (notice: PendingApprovalNotice) => void;
  dismissPendingApprovalNotice: () => void;
  clearSession: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  user: null,
  isAuthenticated: false,
  isHydrated: false,
  pendingApprovalNotice: null,
  setUser: (user) => set({ user, isAuthenticated: Boolean(user) }),
  setHydrated: (isHydrated) => set({ isHydrated }),
  showPendingApprovalNotice: (pendingApprovalNotice) => set({ pendingApprovalNotice }),
  dismissPendingApprovalNotice: () => set({ pendingApprovalNotice: null }),
  clearSession: () => set({ user: null, isAuthenticated: false, pendingApprovalNotice: null }),
}));
