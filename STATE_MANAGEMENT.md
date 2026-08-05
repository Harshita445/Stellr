# Constellation — State Management Strategy

## Two-Layer Approach

```
┌─────────────────────────────────────────────────────────────────────┐
│                      React Query (TanStack Query)                    │
│  Server state: friends list, group list, availability data           │
│  Features: caching, background refetch, optimistic updates,          │
│            stale-while-revalidate, deduplication                     │
│  Provided by: Server Components (initial data) +                     │
│              QueryClient (client-side refetch)                       │
├─────────────────────────────────────────────────────────────────────┤
│                       Zustand (Client State)                         │
│  Client state: auth tokens, UI preferences, selected group,          │
│                realtime connection status, constellation animation   │
│  Features: synchronous access (axios interceptors),                  │
│            persist middleware (localStorage for tokens),             │
│            no provider nesting                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Zustand Store Definitions

### auth-store.ts

```typescript
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  onboardingComplete: boolean;
  // Actions
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  clearAuth: () => void;
}
// Persisted to localStorage via zustand/middleware
```

### friends-store.ts

```typescript
interface FriendsState {
  friendStatuses: Map<string, boolean>;  // friendId → isFree
  selectedFriendId: string | null;
  setFriendStatus: (id: string, isFree: boolean) => void;
  setSelectedFriend: (id: string | null) => void;
}
// Not persisted; ephemeral UI state
```

### groups-store.ts

```typescript
interface GroupsState {
  activeGroupId: string | null;
  constellationCache: Map<string, ConstellationState>;
  setActiveGroup: (id: string | null) => void;
  updateConstellation: (groupId: string, state: ConstellationState) => void;
}
```

---

## Data Fetching Strategy

| Data | Fetch Strategy | Cache TTL | Refetch |
|------|---------------|-----------|---------|
| Own profile | SSR (initial), then stale-while-revalidate | 5 min | On focus |
| Own schedule | SSR (initial), then cache | Infinite (static) | Manual |
| Friends list | SSR, then SWR | 30s | On focus, poll |
| Friend status | Client fetch on dashboard | 30s | Poll |
| Group list | SSR, then SWR | 1 min | On focus |
| Group constellation | Client fetch | 30s | Poll (Phase 1), WS push (Phase 3) |

---

## Why Not Redux?

Redux adds ceremony (action creators, reducers, middleware) that is unnecessary for this application's state complexity. The state is not deeply nested, does not require time-travel debugging, and has clear domain boundaries. Zustand provides equivalent capabilities with ~90% less boilerplate.

## Why React Query for Server State?

1. **Deduplication**: Two components requesting the same friend list get one network request
2. **Optimistic updates**: Remove friend → instantly update UI → revert on error
3. **Staleness**: Configurable per resource type
4. **Background sync**: Tab refocus triggers refresh
5. **Pagination/Cursor**: Built-in for future friend list pagination
