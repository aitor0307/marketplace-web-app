export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  newListing: '/listings/new',
  listing: '/listings/:listingId',
  user: '/users/:userId',
  sendMessage: '/users/:userId/message',
  editProfile: '/profile/edit',
  favorites: '/favorites',
  /** Emailed by auth_ops.approval_url_for; keep the path in sync. */
  approval: '/approvals/:token',
} as const;

/** Builders for parameterised routes — keep in sync with SPA_SUCCESSORS in app/routes/views/__init__.py. */
export const paths = {
  listing: (listingId: number | string) => `/listings/${listingId}`,
  user: (userId: number | string) => `/users/${userId}`,
  sendMessage: (userId: number | string, listingId?: number | string, subject?: string) => {
    const params = new URLSearchParams();
    if (listingId !== undefined) params.set('listingId', String(listingId));
    if (subject) params.set('subject', subject);
    const query = params.toString();
    return `/users/${userId}/message${query ? `?${query}` : ''}`;
  },
};

/** Mirrors ListingForm.conditions in app/forms.py. */
export const LISTING_CONDITIONS = ['New', 'Used', 'Broken'] as const;
export type ListingCondition = (typeof LISTING_CONDITIONS)[number];

/** Spain's provinces + Ceuta and Melilla. Mirrors SPAIN_PROVINCES in app/schemas/locations.py. */
export const SPAIN_PROVINCES = [
  'A Coruña',
  'Albacete',
  'Alicante/Alacant',
  'Almería',
  'Araba/Álava',
  'Asturias',
  'Ávila',
  'Badajoz',
  'Barcelona',
  'Bizkaia',
  'Burgos',
  'Cáceres',
  'Cádiz',
  'Cantabria',
  'Castellón/Castelló',
  'Ceuta',
  'Ciudad Real',
  'Córdoba',
  'Cuenca',
  'Gipuzkoa',
  'Girona',
  'Granada',
  'Guadalajara',
  'Huelva',
  'Huesca',
  'Illes Balears',
  'Jaén',
  'La Rioja',
  'Las Palmas',
  'León',
  'Lleida',
  'Lugo',
  'Madrid',
  'Málaga',
  'Melilla',
  'Murcia',
  'Navarra',
  'Ourense',
  'Palencia',
  'Pontevedra',
  'Salamanca',
  'Santa Cruz de Tenerife',
  'Segovia',
  'Sevilla',
  'Soria',
  'Tarragona',
  'Teruel',
  'Toledo',
  'Valencia/València',
  'Valladolid',
  'Zamora',
  'Zaragoza',
] as const;

/**
 * Ski gear tags offered in the listing form's dropdown (labels in i18n `skiTags`).
 * Stored as these slugs: accent-free Spanish, so listing search still matches them.
 */
export const SKI_TAGS = [
  'esquis',
  'botas',
  'fijaciones',
  'bastones',
  'snowboard',
  'casco',
  'gafas',
  'chaqueta',
  'pantalones',
  'guantes',
  'termica',
  'protecciones',
  'mochila',
  'fundas',
  'travesia',
  'pieles',
  'avalancha',
  'freeride',
  'pista',
  'infantil',
] as const;
export type SkiTag = (typeof SKI_TAGS)[number];

/** Mirrors MAX_LISTING_IMAGES in app/config/base.py. */
export const MAX_LISTING_IMAGES = 10;

export const PRICE_CURRENCY = 'EUR';

export const LANGUAGES = ['en', 'es'] as const;
export type LanguageCode = (typeof LANGUAGES)[number];
