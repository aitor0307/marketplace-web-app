const ACCESS_TOKEN_KEY = 'marketplace.accessToken';
const REFRESH_TOKEN_KEY = 'marketplace.refreshToken';

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // Storage blocked (private mode, etc.): the session just won't survive a reload.
  }
}

/**
 * JWT persistence façade. Swap the storage backend here (cookies, memory)
 * without touching callers.
 */
export const authService = {
  getAccessToken(): string | null {
    return read(ACCESS_TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    return read(REFRESH_TOKEN_KEY);
  },

  hasSession(): boolean {
    return Boolean(read(ACCESS_TOKEN_KEY) || read(REFRESH_TOKEN_KEY));
  },

  setTokens(accessToken: string, refreshToken?: string): void {
    write(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) write(REFRESH_TOKEN_KEY, refreshToken);
  },

  clearTokens(): void {
    write(ACCESS_TOKEN_KEY, null);
    write(REFRESH_TOKEN_KEY, null);
  },
};
