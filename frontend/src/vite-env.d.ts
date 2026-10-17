/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_DEV_PROXY_TARGET?: string;
  /** Build date set by the deploy workflow, e.g. 2026.10.17-0930. */
  readonly VITE_RELEASE_NUMBER?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
