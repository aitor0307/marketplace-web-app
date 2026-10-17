type AnalyticsPayload = Record<string, string | number | boolean | null | undefined>;

/**
 * Stub analytics facade — single instrumentation point for future vendors.
 */
export const analyticsService = {
  track(event: string, payload?: AnalyticsPayload): void {
    if (import.meta.env.DEV) {
      console.debug('[analytics]', event, payload);
    }
  },

  identify(userId: string, traits?: AnalyticsPayload): void {
    if (import.meta.env.DEV) {
      console.debug('[analytics] identify', userId, traits);
    }
  },
};
