import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { listingsApi } from '@/features/listings/api/listings.api';
import type { ListingFilters, NewListingInput } from '@/features/listings/types/listings.types';

export const listingKeys = {
  all: ['listings'] as const,
  list: (filters: ListingFilters) => ['listings', 'list', filters] as const,
  detail: (listingId: number) => ['listings', 'detail', listingId] as const,
};

export function useListings(filters: ListingFilters) {
  return useQuery({
    queryKey: listingKeys.list(filters),
    queryFn: () => listingsApi.list(filters),
  });
}

export function useListing(listingId: number) {
  return useQuery({
    queryKey: listingKeys.detail(listingId),
    queryFn: () => listingsApi.get(listingId),
    enabled: Number.isFinite(listingId),
  });
}

export function useCreateListing() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: NewListingInput) => listingsApi.create(input),
    onSuccess: (listing) => {
      queryClient.setQueryData(listingKeys.detail(listing.id), listing);
      void queryClient.invalidateQueries({ queryKey: listingKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeleteListing() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (listingId: number) => listingsApi.remove(listingId),
    onSuccess: (_data, listingId) => {
      queryClient.removeQueries({ queryKey: listingKeys.detail(listingId) });
      void queryClient.invalidateQueries({ queryKey: listingKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
