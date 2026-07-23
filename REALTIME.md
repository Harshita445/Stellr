# Constellation — Realtime Strategy

## Why Not Full Realtime from Day 1?

The domain has a unique property: availability changes at **deterministic, fixed times** (when classes start/end). There is no continuous change stream. A user's availability status is fully computable from their section's timetable and the current time.

Latency requirements:
- "Am I free right now?" → needs to be accurate to the minute
- "Is my friend free?" → 30-60 second latency is acceptable
- "Is our group free?" → 1-2 minute latency is acceptable

**Decision**: Start with polling (30s interval). The UI impression of "realtime" can be achieved with smooth animations (Framer Motion) on the constellation canvas, even if data is 30s stale.

---

## Phase 1: Polling (MVP)

```
Frontend                        Backend
   │                               │
   │── GET /availability/me ──────→│  (on page load)
   │←── { status, currentClass } ──│
   │                               │
   │── (30s later) ───────────────→│
   │←── { status, currentClass } ──│
   │                               │
   │── ConstellationCanvas ───────→│
   │   polls group endpoint        │
   │   every 30s                   │
```

Implementation: `setInterval` in a React `useEffect` with cleanup. React Query's `refetchInterval` option handles this natively.

---

## Phase 2: Smart Polling

Instead of blind polling every 30s, the client can compute **when the next state change will occur** and poll precisely at that moment:

```typescript
// Client knows: current class ends at 10:00
// Next poll at: 10:00 + 5s buffer
const nextPollTime = new Date(currentClass.ends_at).getTime() + 5000;
setTimeout(refetch, nextPollTime - Date.now());
```

This reduces requests by ~95% (from one per 30s to ~10-15 per day) while providing instant status changes. The 5s buffer accounts for clock skew.

---

## Phase 3: WebSocket

### Architecture

```
┌──────────────────┐     WebSocket      ┌──────────────────────┐
│   Client         │◄═══════════════════│   FastAPI Server      │
│   ┌────────────┐ │                    │   ┌────────────────┐  │
│   │ Zustand    │◄┤                    │   │ WS Manager     │  │
│   │ (local     │ │                    │   │ ┌────────────┐ │  │
│   │  state)    │ │                    │   │ │ Connected  │ │  │
│   └────────────┘ │                    │   │ │ Clients    │ │  │
│   ┌────────────┐ │                    │   │ │ Map        │ │  │
│   │ React Query│◄┤── REST (fallback) ─│──→│ │ user_id →  │ │  │
│   │ (cache)    │ │                    │   │ │ ws         │ │  │
│   └────────────┘ │                    │   │ └────────────┘ │  │
└──────────────────┘                    │   └────────────────┘  │
                                        │   ┌────────────────┐  │
                                        │   │ State Scheduler│  │
                                        │   │ (checks every  │  │
                                        │   │  5 min, pushes │  │
                                        │   │  changes)      │  │
                                        │   └────────────────┘  │
                                        └──────────────────────┘
```

### WebSocket Protocol

```
Client → Server:
  { type: "subscribe", channels: ["group:uuid", "friend:uuid"] }
  { type: "unsubscribe", channels: ["group:uuid"] }
  { type: "ping" }

Server → Client:
  { type: "availability_update", user_id, is_free, since }
  { type: "constellation_update", group_id, members: [...], connections: [...], all_free }
  { type: "friend_status", friend_id, is_free }
  { type: "pong" }
  { type: "error", code: "...", message: "..." }
```

### State Scheduler

A background task (APScheduler or Celery Beat) runs every minute:
1. Query PostgreSQL for class transitions in the next minute
2. For each transition:
   a. Load affected users (all students in the section)
   b. Load affected groups (all groups containing those users)
   c. Compute new constellation states for affected groups
   d. Push `constellation_update` to all subscribed WebSocket clients
   e. Push `availability_update` to all subscribed friend watchers

This avoids the complexity and cost of a full event streaming platform (Kafka, Pulsar) while providing <1 minute update latency.

---

## Fallback Strategy

WebSocket connections can drop (network change, server restart, mobile idle). The client should:

1. Maintain React Query polling as a fallback (30s interval when WS is disconnected)
2. Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
3. On reconnection, re-subscribe to all channels
4. On reconnection, force-refresh all React Query caches
