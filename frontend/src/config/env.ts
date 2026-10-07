export const env = {
  apiUrl: import.meta.env.VITE_API_URL as string | undefined,
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
} as const;

/** API origin without trailing slash; empty string means same-origin. */
export function apiBaseUrl(): string {
  return (env.apiUrl ?? '').replace(/\/$/, '');
}

/** Backend-relative asset paths (e.g. listing images under /static) → absolute URL. */
export function resolveAssetUrl(path?: string | null): string | undefined {
  if (!path) return undefined;
  if (/^https?:\/\//.test(path)) return path;
  return `${apiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
}
