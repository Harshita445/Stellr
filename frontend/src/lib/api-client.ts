const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

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

export interface SectionItem {
  name: string;
  department: string;
  semester: number;
}

export interface UserProfile {
  id: string;
  display_name: string;
  section_code: string | null;
  stellr_code: string | null;
  avatar_url: string | null;
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

export interface GroupMember {
  id: string;
  user_id: string;
  display_name: string;
  section_code: string | null;
  joined_at: string;
}

export interface GroupSummary {
  id: string;
  name: string;
  created_by: string | null;
  member_count: number;
  created_at: string;
}

export interface GroupDetail extends GroupSummary {
  members: GroupMember[];
}

export interface GroupListResponse {
  groups: GroupSummary[];
}

export interface SharedWindow {
  start: string;
  end: string;
}

export interface DashboardScheduleItem {
  course_code: string;
  course_name: string;
  start_time: string;
  end_time: string;
  venue: string | null;
  slot_index: number | null;
}

export interface DashboardFreeWindow {
  start_time: string;
  end_time: string;
  duration_minutes: number;
}

export interface DashboardResponse {
  date: string;
  day_name: string;
  section_code: string | null;
  today_schedule: DashboardScheduleItem[];
  current_class: DashboardScheduleItem & { time_remaining_minutes: number } | null;
  next_class: DashboardScheduleItem | null;
  time_until_next_minutes: number | null;
  free_windows: DashboardFreeWindow[];
}

export interface MemberAvailability {
  user_id: string;
  display_name: string;
  is_free_now: boolean;
}

export interface AvailabilityResponse {
  shared_windows: SharedWindow[];
  current_overlap: boolean;
  next_slot: SharedWindow | null;
  longest_window: SharedWindow | null;
  member_availabilities: MemberAvailability[];
}

export const api = {
  dashboard: {
    get: () => request<DashboardResponse>("GET", "/dashboard"),
  },
  friends: {
    list: () => request<{ friends: FriendRelation[] }>("GET", "/friends"),
    search: (q: string) =>
      request<FriendSearchResult[]>("GET", `/friends/search?q=${encodeURIComponent(q)}`),
    add: (userId: string) =>
      request<AddFriendResult>("POST", `/friends/${userId}`),
    remove: (userId: string) =>
      request<void>("DELETE", `/friends/${userId}`),
    searchByCode: (code: string) =>
      request<FriendSearchResult[]>("GET", `/friends/search-by-code?code=${encodeURIComponent(code)}`),
  },
  availability: {
    compareFriend: (friendId: string) =>
      request<AvailabilityResponse>("GET", `/availability/friend/${friendId}`),
    compareGroup: (groupId: string) =>
      request<AvailabilityResponse>("GET", `/availability/group/${groupId}`),
  },
  groups: {
    list: () => request<GroupListResponse>("GET", "/groups"),
    create: (name: string, memberIds: string[]) =>
      request<GroupDetail>("POST", "/groups", { name, member_ids: memberIds }),
    detail: (groupId: string) =>
      request<GroupDetail>("GET", `/groups/${groupId}`),
    rename: (groupId: string, name: string) =>
      request<GroupDetail>("PATCH", `/groups/${groupId}`, { name }),
    delete: (groupId: string) =>
      request<void>("DELETE", `/groups/${groupId}`),
    addMember: (groupId: string, userId: string) =>
      request<GroupMember>("POST", `/groups/${groupId}/members`, { user_id: userId }),
    removeMember: (groupId: string, userId: string) =>
      request<void>("DELETE", `/groups/${groupId}/members/${userId}`),
  },
  auth: {
    register: (rollNumber: string, displayName: string, sectionCode: string) =>
      request<{
        user: FriendUser & { stellr_code?: string };
        tokens?: { access_token: string; refresh_token: string; device_id: string };
        is_new_account: boolean;
      }>("POST", "/auth/register", {
        roll_number: rollNumber,
        display_name: displayName,
        section_code: sectionCode,
      }),
    claim: (rollNumber: string, displayName: string, sectionCode: string) =>
      request<{
        user: FriendUser & { stellr_code?: string };
        tokens: { access_token: string; refresh_token: string; device_id: string };
      }>("POST", "/auth/claim", {
        roll_number: rollNumber,
        display_name: displayName,
        section_code: sectionCode,
      }),
  },
  sections: {
    list: () =>
      request<{ sections: SectionItem[] }>("GET", "/sections"),
  },
  users: {
    me: () =>
      request<UserProfile>("GET", "/users/me"),
  },
};
