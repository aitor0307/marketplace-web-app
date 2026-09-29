export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  newListing: '/listings/new',
  listing: '/listings/:listingId',
  user: '/users/:userId',
  sendMessage: '/users/:userId/message',
  editProfile: '/profile/edit',
} as const;

/** Builders for parameterised routes — keep in sync with SPA_SUCCESSORS in app/routes/views/__init__.py. */
export const paths = {
  listing: (listingId: number | string) => `/listings/${listingId}`,
  user: (userId: number | string) => `/users/${userId}`,
  sendMessage: (userId: number | string, listingId?: number | string) =>
    `/users/${userId}/message${listingId !== undefined ? `?listingId=${listingId}` : ''}`,
};

/** Mirrors ListingForm.conditions in app/forms.py. */
export const LISTING_CONDITIONS = ['New', 'Used', 'Broken'] as const;
export type ListingCondition = (typeof LISTING_CONDITIONS)[number];

/** Mirrors `states` in app/forms.py. */
export const STATE_OPTIONS = [
  'Lleida',
  'Girona',
  'Barcelona',
  'Madrid',
  'Bizkaia',
  'Gipuzkoa',
] as const;

export const PRICE_CURRENCY = 'EUR';

export const LANGUAGES = ['en', 'es'] as const;
export type LanguageCode = (typeof LANGUAGES)[number];
