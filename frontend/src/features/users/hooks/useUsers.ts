import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '@/features/users/api/users.api';
import type { UpdateProfileRequest } from '@/features/users/types/users.types';
import { useSessionStore } from '@/store/sessionStore';

export const userKeys = {
  detail: (userId: number) => ['users', userId] as const,
  listings: (userId: number) => ['users', userId, 'listings'] as const,
};

export function useUser(userId: number) {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: () => usersApi.get(userId),
    enabled: Number.isFinite(userId),
  });
}

export function useUserListings(userId: number) {
  return useQuery({
    queryKey: userKeys.listings(userId),
    queryFn: () => usersApi.listings(userId),
    enabled: Number.isFinite(userId),
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const userId = useSessionStore((s) => s.user?.id);
  const setUser = useSessionStore((s) => s.setUser);

  return useMutation({
    mutationFn: (payload: UpdateProfileRequest) => usersApi.update(userId as number, payload),
    onSuccess: (user) => {
      setUser(user);
      queryClient.setQueryData(userKeys.detail(user.id), user);
      // Author cards embedded in listings carry the old name/location.
      void queryClient.invalidateQueries({ queryKey: ['listings'] });
    },
  });
}
