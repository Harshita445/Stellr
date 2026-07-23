const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface FriendUser {
  id: string;
  display_name: string;
  section_code: string | null;
}

export interface FriendRelation {
  id: string;
  user: FriendUser;
}

export interface FriendSearchResult {
  id: string;
  display_name: string;
  section_code: string | null;
}

export interface AddFriendResult {
  friendship_id: string;
  user: FriendUser;
}

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function getTokens(): { accessToken: string; deviceId: string } | null {
  if (typeof window === "undefined") return null;
  const at = localStorage.getItem("access_token");
  const did = localStorage.getItem("device_id");
  if (!at || !did) return null;
  return { accessToken: at, deviceId: did };
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const tokens = getTokens();
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (tokens) {
    headers["Authorization"] = `Bearer ${tokens.accessToken}`;
    headers["X-Device-ID"] = tokens.deviceId;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let code = "UNKNOWN";
    let message = "Request failed";
    try {
      const err = await res.json();
      code = err.error?.code || code;
      message = err.error?.message || message;
    } catch {}
    throw new ApiError(res.status, code, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  friends: {
    list: () => request<{ friends: FriendRelation[] }>("GET", "/friends"),
    search: (q: string) =>
      request<FriendSearchResult[]>("GET", `/friends/search?q=${encodeURIComponent(q)}`),
    add: (userId: string) =>
      request<AddFriendResult>("POST", `/friends/${userId}`),
    remove: (userId: string) =>
      request<void>("DELETE", `/friends/${userId}`),
  },
};
