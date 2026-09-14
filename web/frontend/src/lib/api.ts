// Thin API client for the FastAPI backend. The session token is kept in memory
// (and mirrored to sessionStorage so a refresh mid-session survives) and sent
// as the X-Session-Id header.
const TOKEN_KEY = "tju-session";

// Base URL of the backend. Empty by default so requests hit the same origin —
// the dev server proxies /api to :8000, and a Netlify rewrite can do the same in
// production. Set VITE_API_BASE at build time to call an absolute backend URL
// instead (e.g. a Cloudflare Tunnel address); the backend must then allow this
// site in CORS_ORIGINS.
const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

function getToken(): string | null {
  try {
    return sessionStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}
function setToken(token: string | null): void {
  try {
    if (token) sessionStorage.setItem(TOKEN_KEY, token);
    else sessionStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("X-Session-Id", token);

  const res = await fetch(API_BASE + path, { ...init, headers });
  const isJson = res.headers.get("content-type")?.includes("application/json");
  const body = isJson ? await res.json() : null;
  if (!res.ok) {
    const detail = (body && (body.detail as string)) || `请求失败 (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return body as T;
}

export interface UserInfo {
  name: string;
  stuid?: string;
  balance?: string;
}

export interface CardRecord {
  time: string;
  id?: string;
  type?: string;
  amount: string;
  place?: string;
}

export interface Stats {
  empty: boolean;
  summary?: {
    total: number;
    count: number;
    daily_average: number;
    per_transaction_average: number;
    active_days: number;
    first_day: string;
    last_day: string;
  };
  by_type?: { type: string; count: number; sum: number; mean: number }[];
  by_month?: { month: number; count: number; sum: number }[];
  by_time_slot?: { slot: string; count: number; sum: number; mean: number }[];
  top_places?: { place: string; count: number; sum: number }[];
  extremes?: Record<string, { amount: number; time: string; place: string; type: string }>;
  daily_series?: { date: string; amount: number }[];
}

export const api = {
  async login(username: string, password: string): Promise<UserInfo> {
    const data = await request<{ token: string; user: UserInfo }>("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setToken(data.token);
    return data.user;
  },

  async records(
    year?: string,
    refresh = false,
  ): Promise<{ year: string; records: CardRecord[]; stats: Stats }> {
    const params = new URLSearchParams();
    if (year) params.set("year", year);
    if (refresh) params.set("refresh", "true");
    const q = params.toString();
    return request(`/api/records${q ? `?${q}` : ""}`);
  },

  /** Export the year's records as CSV. Desktop: native Save dialog via the
   *  pywebview bridge; browser/local-web: a normal file download. */
  async exportCsv(stuid: string, year: string): Promise<string | null> {
    const bridge = (window as unknown as { pywebview?: PyWebview }).pywebview;
    if (bridge?.api?.export_csv) {
      const res = await bridge.api.export_csv(stuid, year);
      if (!res.ok) throw new Error(res.error || "导出失败");
      return res.path ?? null;
    }
    // Browser / local-web fallback: fetch with auth header, then save the blob.
    const res = await fetch(`${API_BASE}/api/export?year=${encodeURIComponent(year)}`, {
      headers: getToken() ? { "X-Session-Id": getToken()! } : {},
    });
    if (!res.ok) throw new Error(`导出失败 (${res.status})`);
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = `tju-${stuid}-${year}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    return null;
  },

  async logout(): Promise<void> {
    try {
      await request("/api/logout", { method: "POST" });
    } finally {
      setToken(null);
    }
  },

  hasSession(): boolean {
    return getToken() !== null;
  },
};
