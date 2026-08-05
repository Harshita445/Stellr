# Constellation — Architecture

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                            CLIENT TIER                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Next.js 15 (App Router)                                        │  │
│  │  ├── SSR Pages (dashboard, friends, groups)                     │  │
│  │  ├── React Server Components for data-fetching pages            │  │
│  │  └── Client Components for interactive features (constellation) │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                      HTTPS (API) / WSS (Realtime)
                                    │
┌────────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY TIER                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Reverse Proxy (Nginx / Caddy)                                 │  │
│  │  ├── TLS termination                                            │  │
│  │  ├── Rate limiting                                              │  │
│  │  ├── Request routing (/api/* → FastAPI, /* → Next.js)          │  │
│  │  └── WebSocket upgrade handling                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
┌────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION TIER                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Stateless, horizontal scale)                          │  │
│  │  ├── Auth Service     │  Timetable Service (Admin)              │  │
│  │  ├── User Service     │  Social Graph Service                   │  │
│  │  └── Availability Service (Core business logic)                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
┌────────────────────────────────────────────────────────────────────────┐
│                           DATA TIER                                    │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  PostgreSQL (Primary)           │  │  Redis (Future: cache/pubsub)│ │
│  │  ├── Users & Devices            │  │  ├── Availability cache     │ │
│  │  ├── Sections & Courses         │  │  ├── WebSocket pub/sub      │ │
│  │  ├── Timetable Entries          │  │  └── Rate limit counters    │ │
│  │  ├── Friend Graph               │  │                              │ │
│  │  └── Groups & Memberships       │  │                              │ │
│  └─────────────────────────────────┘  └──────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

**Key architectural principle**: The system is a **modular monolith** — a single deployable unit with well-defined internal service boundaries. This is the correct choice for college scale (5K–15K users). The service boundaries are designed such that extraction into separate microservices (if ever needed) requires only moving Python packages to new processes.

---

## System Diagram

```
                    ┌──────────────┐
                    │  Excel File  │  (Imported once by admin)
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Parser &    │
                    │  Validator   │  (Background task)
                    └──────┬───────┘
                           │
                           ▼
               ┌─────────────────────┐
               │   PostgreSQL        │
               │   ┌─────────────┐   │
               │   │ sections    │   │
               │   │ courses     │   │
               │   │ timeslots   │◄──┤──── Timetable data (read-only after import)
               │   │ tt_entries  │   │
               │   ├─────────────┤   │
               │   │ users       │   │
               │   │ devices     │   │
               │   ├─────────────┤   │
               │   │ friends     │   │
               │   │ groups      │   │
               │   │ grp_members │   │
               │   └─────────────┘   │
               └─────────────────────┘
                        ▲
                        │
               ┌────────┴────────┐
               │  Availability   │
               │  Service        │  (Query logic, time intersection)
               └────────┬────────┘
                        │
          ┌─────────────┼──────────────┐
          │             │              │
    ┌─────▼────┐ ┌─────▼────┐  ┌──────▼──────┐
    │ REST API │ │ WebSocket│  │ Constellation│
    │(FastAPI) │ │ (Future) │  │ Visualization│
    └─────┬────┘ └──────────┘  └──────┬───────┘
          │                            │
          └──────────┬─────────────────┘
                     │
              ┌──────▼──────┐
              │  Next.js 15 │  (SSR + client components)
              │  Frontend   │
              └─────────────┘
```

---

## Service Boundaries

### Identity & Auth Service
```
Scope: Registration, device verification, token lifecycle
Dependencies: users table, devices table
No dependencies on: timetable, social graph
Reason: Auth is the outermost layer; must operate independently.
```

### Timetable Service (Admin only)
```
Scope: Excel parsing, validation, normalization, bulk insert
Dependencies: sections, courses, timeslots, timetable_entries
Isolation: Never invoked during user-facing requests.
            Only triggered by admin action.
            Import result is validated and stored before any user sees data.
```

### User Profile Service
```
Scope: Profile CRUD, section assignment, onboarding flow
Dependencies: users table, sections table
Design note: Section assignment happens once during onboarding.
             Changing section should be an admin-mediated action
             (to prevent timetable manipulation).
```

### Social Graph Service
```
Scope: Friend management, group CRUD, membership
Dependencies: users, friends, groups, group_members
Key invariant: Friendship is bidirectional (single row).
               Group membership requires membership (join request flow in v2).
```

### Availability Service (Core Business Logic)
```
Scope: Individual status, friend comparison, group overlap
Dependencies: timetable_entries, timeslots, users (for section lookup)
This is the most query-intensive service.
Must be optimized for read performance.
Cache-friendly (timetable is static for the semester).
```

### Service Dependency Graph
```
Auth ──> User ──> Social Graph
                    │
                    ▼
              Availability (reads from Timetable + Social Graph)
                    │
                    ▼
              Realtime (wraps Availability + pushes to WebSocket clients)
```

---

## Frontend Architecture

### Route Tree with Data Requirements

```
/                        → Public: Login screen
                            ├── Data: none
                            └── Auth: none

/onboarding              → Authenticated: Section selection
                            ├── Data: sections list
                            └── Auth: valid session

/dashboard               → Authenticated: Home
                            ├── Data: own availability (current status,
                            │         next class, next free slot)
                            └── Auth: JWT + section assigned

/friends                 → Authenticated: Friend list
                            ├── Data: friend list with availability states
                            └── Auth: JWT

/friends/[id]            → Authenticated: Comparison view
                            ├── Data: common free slots for the day
                            └── Auth: JWT + must be friends

/groups                  → Authenticated: Group list
                            ├── Data: groups + next overlap per group
                            └── Auth: JWT

/groups/[id]             → Authenticated: Group detail + constellation
                            ├── Data: member list, member availability,
                            │         connections, next overlap
                            └── Auth: JWT + must be member

/admin/import            → Admin: Timetable upload
                            ├── Data: none (upload form)
                            └── Auth: JWT + admin role
```

### Component Architecture by Responsibility

```
Presentation Layer (Server Components where possible)
├── Layout shell (navigation, header, star background)
├── ScheduleTimeline (day/week view of timetable)
├── FriendCard (avatar, name, status indicator)
├── GroupCard (name, member count, constellation preview)
├── ConstellationCanvas (core interactive visualization)
│   ├── Star (individual member node)
│   ├── ConnectionLine (edge between free members)
│   └── ConstellationLabel (group name, all-free status)

State Layer (Client Components where interactivity needed)
├── CurrentStatusCard (polls availability, animated transitions)
├── FriendSearchBox (debounced search)
├── MemberList (reorderable, shows live status)
├── GroupCreateDialog (multi-step form)

Data Layer (Hooks + Stores)
├── useAvailability(userId) → { status, currentClass, nextEvent }
├── useGroupConstellation(groupId) → { members[], connections[], allFree }
├── useFriendStatus(friendId) → { isFree, lastChecked }
```

### Rendering Strategy

| Page Type | Strategy | Rationale |
|-----------|----------|-----------|
| Dashboard | SSR + Client hydration | Fast initial paint, then live updates |
| Friends list | SSR with streaming | List can be large; stream results |
| Friends detail | SSR | Static schedule comparison |
| Group detail | SSR shell + Client constellation | Canvas needs client rendering |
| Groups list | SSR | Simple list, no realtime needed |
| Login/Onboarding | Static | No dynamic data needed |

---

## Backend Architecture

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ROUTERS (api/v1/*)                     │
│  Thin layer: parse request, validate (Pydantic), call       │
│  service, format response                                   │
├─────────────────────────────────────────────────────────────┤
│                      SERVICES (Business Logic)              │
│  AvailabilityService:                                       │
│    - is_free_at(user_id, datetime) → bool                  │
│    - find_common_slots(user_ids, date) → list[TimeRange]    │
│    - next_common_overlap(group_id) → TimeRange | None       │
│                                                             │
│  FriendService:                                             │
│    - add_friend(user_id, friend_id) → void                  │
│    - get_friends_with_status(user_id) → list[FriendStatus]  │
│                                                             │
│  GroupService:                                              │
│    - create_group(creator, name, member_ids) → Group        │
│    - get_constellation_state(group_id) → ConstellationState │
├─────────────────────────────────────────────────────────────┤
│                  REPOSITORIES (Data Access)                 │
│  AvailabilityRepository:                                    │
│    - get_timetable_entries(section_id, day) → list[Entry]  │
│                                                             │
│  UserRepository, FriendRepository, GroupRepository          │
├─────────────────────────────────────────────────────────────┤
│                      MODELS (SQLAlchemy)                    │
│  User, Device, Section, Course, Timeslot,                   │
│  TimetableEntry, Friend, Group, GroupMember                 │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Injection Pattern

```python
# FastAPI dependency injection wires service -> repository -> session

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_availability_service(
    db: AsyncSession = Depends(get_db)
) -> AvailabilityService:
    repo = AvailabilityRepository(db)
    return AvailabilityService(repo)
```

This keeps services testable (unit tests inject mock repositories) and allows swapping repository implementations without changing business logic.

### Key Algorithm: Group Overlap Detection

```
Input: Set of user_ids in a group, a target date
Output: List of common free time ranges

Algorithm:
1. For each user, get their section_id
2. For each section_id, fetch all timetable_entries for the target day
3. Compute busy time ranges per user: union of [start, end) for each entry
4. Invert busy ranges to get free ranges per user (bounded by 08:00 - 20:00)
5. Compute intersection of free ranges across all users
6. Return sorted list of intersections

Complexity: O(N * M + N * K) where N = members, M = entries per member,
            K = free slots per member. N ≤ 15, M ≤ 8, K ≤ 12.
            Total: negligible (≤ 200 operations).
```

---

## Folder Structure

```
constellation/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── onboarding/
│   │   │   │       └── page.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── friends/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx
│   │   │   │   ├── groups/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx
│   │   │   │   └── admin/
│   │   │   │       └── import/
│   │   │   │           └── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/              # shadcn primitives (button, card, dialog, etc.)
│   │   │   ├── layout/          # AppShell, Sidebar, BottomNav, TopBar
│   │   │   ├── auth/            # LoginForm, DeviceRegister, SectionSelect
│   │   │   ├── schedule/        # Timeline, ScheduleCard, CurrentStatusBadge
│   │   │   ├── friends/         # FriendCard, FriendList, FriendSearch
│   │   │   ├── groups/          # GroupCard, GroupList, MemberRow, CreateGroupForm
│   │   │   └── constellation/   # Canvas, StarNode, EdgeLine, useConstellation
│   │   ├── hooks/               # useAuth, useFriends, useGroups, useAvailability
│   │   ├── lib/                 # api-client, auth-utils, time-utils, constants
│   │   ├── store/               # Zustand stores (auth, friends, groups, availability)
│   │   └── types/               # api.ts, user.ts, group.ts, timetable.ts
│   ├── public/
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── friends.py
│   │   │   │   ├── groups.py
│   │   │   │   ├── availability.py
│   │   │   │   └── admin.py
│   │   │   └── deps.py          # Shared dependencies (get_db, get_current_user)
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   ├── security.py      # JWT encode/decode, passwordless auth
│   │   │   └── database.py      # Engine, session factory
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic
│   │   ├── repositories/        # Data access
│   │   └── utils/
│   │       ├── timetable_parser.py  # Excel parsing (openpyxl)
│   │       └── time_utils.py        # Slot intersection, day helpers
│   ├── alembic/                 # Migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Summary of Architecture Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Modular monolith** over microservices | College scale (5-15K users) does not justify microservices complexity. Service boundaries are clearly defined for future extraction. |
| 2 | **PostgreSQL** over NoSQL | Timetable data is highly relational (sections → courses → timeslots). Availability queries benefit from indexed joins. |
| 3 | **Normalized schema** over JSONB | Query performance, referential integrity, no data duplication. JSONB would require application-level consistency. |
| 4 | **Device-based auth** over passwords | Eliminates password management, phishing risk. Appropriate for closed campus environment. |
| 5 | **JWT + refresh tokens** over sessions | Stateless authentication enables horizontal scaling without shared session store. |
| 6 | **Zustand + React Query** over Redux | Lower boilerplate, better performance, synchronous auth token access, automatic server state caching. |
| 7 | **Canvas rendering** over SVG/DOM | Better performance for 50+ animated stars, direct frame control, no DOM overhead. |
| 8 | **Application-level time intersection** over SQL | More testable, maintainable, and debuggable than complex SQL with range types. |
| 9 | **Polling → WebSocket progression** | MVP can launch faster without WebSocket complexity. Domain (fixed schedule) makes polling efficient. |
| 10 | **Background task import** | Timetable import is heavy and infrequent (once/semester). Should never block user requests. |
| 11 | **SSR-first with client islands** | Next.js App Router enables fast initial paint with Server Components. Constellation canvas is the only required client component. |
| 12 | **Single friendship row** (bidirectional) | Half the rows of directional friendship, simpler query patterns. |
