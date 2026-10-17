import type { ListingCondition } from '@/config/constants';

/** Mirrors ListListingsQuery in app/schemas/listings.py. */
export type ListingFilters = {
  /** Fuzzy search over title, tags and description. */
  q?: string;
  condition?: ListingCondition | '';
  /** Exact tag, usually one of SKI_TAGS. */
  tag?: string;
  price_min?: string;
  price_max?: string;
};

/** Mirrors CreateListingPayload + the repeated multipart `images` field. */
export type NewListingInput = {
  title: string;
  body: string;
  condition: ListingCondition;
  price: number;
  tags: string[];
  /** The first one becomes the cover. */
  images: File[];
};
