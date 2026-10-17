import { apiClient } from '@/services/apiClient';
import type { Listing } from '@/types/models';

/** Favorites live in the user's external_data.favorite_listing_ids. */
export type FavoriteIdsResponse = { favorite_listing_ids: number[] };

export const favoritesApi = {
  add(listingId: number): Promise<FavoriteIdsResponse & { created: boolean }> {
    return apiClient(`/api/v1/favorites/${listingId}`, { method: 'POST' });
  },

  remove(listingId: number): Promise<FavoriteIdsResponse & { removed: boolean }> {
    return apiClient(`/api/v1/favorites/${listingId}`, { method: 'DELETE' });
  },

  /** The signed-in user's favorites, most recently added first. */
  listMine(): Promise<Listing[]> {
    return apiClient<{ listings: Listing[] }>('/api/v1/favorites').then((res) => res.listings);
  },
};
