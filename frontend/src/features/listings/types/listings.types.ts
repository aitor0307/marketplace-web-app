import type { ListingCondition } from '@/config/constants';

/** Mirrors ListListingsQuery in app/schemas/listings.py. */
export type ListingFilters = {
  condition?: ListingCondition | '';
  price_min?: string;
  price_max?: string;
};

/** Mirrors CreateListingPayload + the multipart `image` field. */
export type NewListingInput = {
  title: string;
  body: string;
  condition: ListingCondition;
  price: number;
  tags: string[];
  image: File;
};
