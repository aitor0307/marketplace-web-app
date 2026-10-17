import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { favoritesApi, type FavoriteIdsResponse } from '@/features/favorites/api/favorites.api';
import { useSessionStore } from '@/store/sessionStore';
import type { Listing } from '@/types/models';

export const favoriteKeys = {
  forUser: (userId: number) => ['users', userId, 'favorites'] as const,
};

/** The signed-in user's favorites (the only ones the API will return). */
export function useMyFavorites() {
  const userId = useSessionStore((s) => s.user?.id);
  return useQuery({
    queryKey: favoriteKeys.forUser(userId ?? -1),
    queryFn: () => favoritesApi.listMine(),
    enabled: userId !== undefined,
  });
}

export function useIsFavorite(listingId: number) {
  const { data: favorites } = useMyFavorites();
  return favorites?.some((fav) => fav.id === listingId) ?? false;
}

type ToggleFavoriteVars = { listing: Listing; isFavorite: boolean };

/** Adds or removes, updating the favorites list optimistically so every heart flips at once. */
export function useToggleFavorite() {
  const queryClient = useQueryClient();
  const userId = useSessionStore((s) => s.user?.id);
  const queryKey = favoriteKeys.forUser(userId ?? -1);

  return useMutation({
    mutationFn: ({ listing, isFavorite }: ToggleFavoriteVars): Promise<FavoriteIdsResponse> =>
      isFavorite ? favoritesApi.remove(listing.id) : favoritesApi.add(listing.id),
    onMutate: async ({ listing, isFavorite }) => {
      await queryClient.cancelQueries({ queryKey });
      const previous = queryClient.getQueryData<Listing[]>(queryKey);
      queryClient.setQueryData<Listing[]>(queryKey, (old = []) =>
        isFavorite ? old.filter((fav) => fav.id !== listing.id) : [listing, ...old],
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      queryClient.setQueryData(queryKey, context?.previous);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey });
    },
  });
}
