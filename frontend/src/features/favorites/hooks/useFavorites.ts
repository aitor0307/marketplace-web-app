import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { favoritesApi } from '@/features/favorites/api/favorites.api';
import { useSessionStore } from '@/store/sessionStore';

export const favoriteKeys = {
  forUser: (userId: number) => ['users', userId, 'favorites'] as const,
};

/** The signed-in user's favorites (the only ones the API will return). */
export function useMyFavorites() {
  const userId = useSessionStore((s) => s.user?.id);
  return useQuery({
    queryKey: favoriteKeys.forUser(userId ?? -1),
    queryFn: () => favoritesApi.listForUser(userId as number),
    enabled: userId !== undefined,
  });
}

export function useAddFavorite() {
  const queryClient = useQueryClient();
  const userId = useSessionStore((s) => s.user?.id);
  return useMutation({
    mutationFn: (listingId: number) => favoritesApi.add(listingId),
    onSuccess: () => {
      if (userId !== undefined)
        void queryClient.invalidateQueries({ queryKey: favoriteKeys.forUser(userId) });
    },
  });
}
