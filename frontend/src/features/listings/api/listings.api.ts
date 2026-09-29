import { apiClient } from '@/services/apiClient';
import type { ListingFilters, NewListingInput } from '@/features/listings/types/listings.types';
import type { Listing } from '@/types/models';

export const listingsApi = {
  list(filters: ListingFilters = {}): Promise<Listing[]> {
    return apiClient<{ listings: Listing[] }>('/api/v1/listings', {
      query: filters,
      auth: false,
    }).then((res) => res.listings);
  },

  get(listingId: number): Promise<Listing> {
    return apiClient<{ listing: Listing }>(`/api/v1/listings/${listingId}`, { auth: false }).then(
      (res) => res.listing,
    );
  },

  create(input: NewListingInput): Promise<Listing> {
    const form = new FormData();
    form.append('title', input.title);
    form.append('body', input.body);
    form.append('condition', input.condition);
    form.append('price', String(input.price));
    input.tags.forEach((tag) => form.append('tags', tag));
    form.append('image', input.image);
    return apiClient<{ listing: Listing }>('/api/v1/listings', { method: 'POST', body: form }).then(
      (res) => res.listing,
    );
  },

  remove(listingId: number): Promise<void> {
    return apiClient<void>(`/api/v1/listings/${listingId}`, { method: 'DELETE' });
  },
};
