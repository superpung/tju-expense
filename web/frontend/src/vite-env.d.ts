/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Absolute backend base URL; empty = same-origin (dev proxy / local server). */
  readonly VITE_API_BASE?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

/** pywebview JS bridge, present only inside the desktop app. */
interface PyWebview {
  api?: {
    export_csv?: (
      stuid: string,
      year: string,
    ) => Promise<{ ok: boolean; path?: string; error?: string }>;
  };
}
