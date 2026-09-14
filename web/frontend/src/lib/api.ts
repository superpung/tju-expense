// Thin API client for the FastAPI backend. The session token is kept in memory
// (and mirrored to sessionStorage so a refresh mid-session survives) and sent
// as the X-Session-Id header.
const TOKEN_KEY = "tju-session";

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

  const res = await fetch(path, { ...init, headers });
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

  async records(year?: string): Promise<{ year: string; records: CardRecord[]; stats: Stats }> {
    const q = year ? `?year=${encodeURIComponent(year)}` : "";
    return request(`/api/records${q}`);
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
