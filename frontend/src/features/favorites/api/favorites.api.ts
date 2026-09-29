import { apiClient } from '@/services/apiClient';
import type { Listing } from '@/types/models';

export const favoritesApi = {
  add(listingId: number): Promise<{ created: boolean }> {
    return apiClient<{ created: boolean }>(`/api/v1/favorites/${listingId}`, { method: 'POST' });
  },

  /** Self only — the API answers 403 for anyone else's favorites. */
  listForUser(userId: number): Promise<Listing[]> {
    return apiClient<{ listings: Listing[] }>(`/api/v1/users/${userId}/favorites`).then(
      (res) => res.listings,
    );
  },
};
