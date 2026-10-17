import { apiBaseUrl } from '@/config/env';
import { ApiError, type ApiErrorBody, type RequestOptions } from '@/types/api';
import { authService } from '@/services/authService';
import { useSessionStore } from '@/store/sessionStore';

async function parseError(response: Response): Promise<ApiError> {
  let body: ApiErrorBody | undefined;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    body = undefined;
  }

  if (Array.isArray(body?.message)) {
    const fieldErrors: Record<string, string> = {};
    for (const item of body.message) {
      const field = String(item.loc[0] ?? '');
      if (field && !fieldErrors[field]) fieldErrors[field] = item.msg;
    }
    return new ApiError(response.status, body.message[0]?.msg ?? 'Invalid request', fieldErrors);
  }

  const message = body?.error ?? body?.message ?? (response.statusText || 'Request failed');
  return new ApiError(response.status, message);
}

/** jwt_verify reports an expired token as 400 "Token has expired!", not 401. */
function isExpiredToken(error: ApiError): boolean {
  return error.status === 401 || /token has expired/i.test(error.message);
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = path.startsWith('http')
    ? path
    : `${apiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
  if (!query) return url;

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function send(
  path: string,
  options: RequestOptions,
  token: string | null,
): Promise<Response> {
  const { method = 'GET', body, query, headers = {}, signal } = options;
  const requestHeaders: Record<string, string> = { Accept: 'application/json', ...headers };
  const isForm = body instanceof FormData;

  if (body !== undefined && !isForm) requestHeaders['Content-Type'] = 'application/json';
  if (token) requestHeaders.Authorization = `Bearer ${token}`;

  return fetch(buildUrl(path, query), {
    method,
    headers: requestHeaders,
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    signal,
  });
}

let refreshInFlight: Promise<string | null> | null = null;

/** Single-flight refresh: concurrent 401s share one /auth/refresh call. */
function refreshAccessToken(): Promise<string | null> {
  refreshInFlight ??= (async () => {
    const refreshToken = authService.getRefreshToken();
    if (!refreshToken) return null;
    const response = await send('/api/v1/auth/refresh', { method: 'POST' }, refreshToken);
    if (!response.ok) return null;
    const { access_token } = (await response.json()) as { access_token: string };
    authService.setTokens(access_token);
    return access_token;
  })().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

/**
 * Shared fetch wrapper. Feature API modules must use this — never call fetch from screens.
 */
export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const useAuth = options.auth ?? true;
  let response = await send(path, options, useAuth ? authService.getAccessToken() : null);

  if (!response.ok) {
    let error = await parseError(response);

    if (useAuth && isExpiredToken(error) && authService.getRefreshToken()) {
      const freshToken = await refreshAccessToken();
      if (!freshToken) {
        authService.clearTokens();
        useSessionStore.getState().clearSession();
        throw error;
      }
      response = await send(path, options, freshToken);
      if (response.ok) return parse<T>(response);
      error = await parseError(response);
    }

    throw error;
  }

  return parse<T>(response);
}

async function parse<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
