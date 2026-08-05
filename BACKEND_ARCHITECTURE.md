# Constellation — Backend Architecture

**Stack**: FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, Pydantic v2, JWT, Redis

---

## Table of Contents

1. [Architecture Philosophy](#1-architecture-philosophy)
2. [Folder Structure](#2-folder-structure)
3. [Layer Architecture](#3-layer-architecture)
4. [Database Layer](#4-database-layer)
5. [Repository Layer](#5-repository-layer)
6. [Service Layer](#6-service-layer)
7. [API Layer](#7-api-layer)
8. [Pydantic Schemas](#8-pydantic-schemas)
9. [Dependency Injection](#9-dependency-injection)
10. [Middleware Stack](#10-middleware-stack)
11. [Authentication System](#11-authentication-system)
12. [Timetable Engine](#12-timetable-engine)
13. [Availability Engine](#13-availability-engine)
14. [Caching Architecture](#14-caching-architecture)
15. [Error Handling](#15-error-handling)
16. [Logging & Monitoring](#16-logging--monitoring)
17. [Configuration](#17-configuration)
18. [Security Design](#18-security-design)
19. [Future Scaling Plan](#19-future-scaling-plan)

---

## 1. Architecture Philosophy

### Principles

1. **Routes are thin, services are thick.** Route handlers never contain business logic. They parse the request, validate input (via Pydantic), call a service, format the response. That is all.

2. **Services own the business logic.** A service operates on domain concepts, not HTTP concepts. It receives primitives or domain models, not request objects. It is fully testable without HTTP.

3. **Repositories own data access.** Services never touch SQLAlchemy directly. Repositories return domain models or raw data structures. This enables:
   - Swapping SQL for cache (Redis) without service changes
   - Unit testing services with mock repositories
   - Changing the ORM without touching business logic

4. **Pydantic schemas decouple layers.**
   - `schemas/requests/` — validated input from the client
   - `schemas/responses/` — structured output to the client
   - `schemas/internal/` — data transfer between services and repositories
   - `schemas/events/` — message payloads for realtime/async

5. **Modules are cohesive, loosely coupled.** Each module (auth, users, friends, groups, availability, timetables) is a self-contained package with its own services, repositories, schemas, and API routes. Cross-module communication happens through imports of public service interfaces, never through shared mutable state.

6. **Async by default.** All database operations, cache operations, and external I/O use `async/await`. CPU-bound tasks (timetable parsing) run in a thread pool executor.

7. **Fail fast, fail loudly.** Validation errors are caught at the boundary (Pydantic). Service errors are typed exceptions. Unhandled errors propagate to global exception handlers that return consistent error JSON. No silent failures.

### Module Dependency Graph

```
                     ┌──────────────────────┐
                     │       config         │
                     │   (global settings)  │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │        core          │
                     │  (database, security, │
                     │   cache, exceptions) │
                     └──────────┬───────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
  ┌───────────────┐   ┌─────────────────┐   ┌──────────────────┐
  │     auth      │   │     users       │   │    timetables    │
  │ (no deps)     │   │ (depends: auth) │   │ (admin only)     │
  └───────────────┘   └────────┬────────┘   └──────────────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │   friends       │
                      │ (depends: users)│
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │    groups       │
                      │ (depends: friends│
                      │  + timetables)  │
                      └────────┬────────┘
                               │
                               ▼
                      ┌──────────────────────┐
                      │   availability       │
                      │ (depends: users,     │
                      │  friends, groups,    │
                      │  timetables)         │
                      └────────┬─────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
           ┌────────────────┐   ┌──────────────────┐
           │ notifications  │   │   realtime       │
           │ (depends:      │   │ (depends: avail, │
           │  availability) │   │  groups, ws)     │
           └────────────────┘   └──────────────────┘
```

---

## 2. Folder Structure

```
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app factory
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Pydantic Settings (env → settings)
│   │   ├── database.py                  # Engine, async session factory
│   │   ├── cache.py                     # Redis client, connection pool
│   │   ├── security.py                  # JWT encode/decode, hashing
│   │   ├── exceptions.py               # Domain exception hierarchy
│   │   ├── error_handlers.py            # Global exception → JSON
│   │   ├── middleware.py                # CORS, rate limit, request ID
│   │   └── logging.py                   # Structured JSON logger
│   │
│   ├── models/
│   │   ├── __init__.py                  # Re-export all models
│   │   ├── base.py                      # DeclarativeBase, common mixins
│   │   ├── user.py
│   │   ├── device.py
│   │   ├── section.py
│   │   ├── course.py
│   │   ├── timeslot.py
│   │   ├── timetable_entry.py
│   │   ├── friend.py
│   │   ├── group.py
│   │   └── group_member.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py                    # Shared: Pagination, Error, ID
│   │   ├── auth/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── users/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── friends/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── groups/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── availability/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── timetables/
│   │   │   ├── requests.py              # File upload
│   │   │   └── responses.py             # Import status, schedule
│   │   ├── notifications/
│   │   │   └── responses.py
│   │   └── realtime/
│   │       └── events.py                # WebSocket message schemas
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract CRUD repository
│   │   ├── user_repository.py
│   │   ├── device_repository.py
│   │   ├── section_repository.py
│   │   ├── course_repository.py
│   │   ├── timeslot_repository.py
│   │   ├── timetable_entry_repository.py
│   │   ├── friend_repository.py
│   │   ├── group_repository.py
│   │   └── group_member_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── friend_service.py
│   │   ├── group_service.py
│   │   ├── availability_service.py      # Core orchestration
│   │   ├── timetable_parser_service.py  # Excel parsing (sync, thread pool)
│   │   ├── timetable_import_service.py  # Orchestrates parse → normalize → store
│   │   ├── timetable_query_service.py   # Read-only timetable lookups
│   │   ├── notification_service.py
│   │   └── realtime_service.py          # WebSocket state manager
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                      # Shared DI: get_db, get_current_user, etc.
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # Aggregate all v1 routers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── friends.py
│   │   │   ├── groups.py
│   │   │   ├── availability.py
│   │   │   ├── timetables.py
│   │   │   ├── notifications.py
│   │   │   └── admin.py
│   │   └── ws/
│   │       ├── __init__.py
│   │       └── handler.py               # WebSocket connection manager
│   │
│   ├── worker/
│   │   ├── __init__.py
│   │   └── tasks.py                     # Background task definitions
│   │
│   └── utils/
│       ├── __init__.py
│       ├── time_utils.py                # Slot intersection, day helpers, week boundaries
│       └── device_fingerprint.py        # SHA-256 fingerprinting
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures: test DB, Redis mock, client
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_availability_service.py
│   │   ├── test_friend_service.py
│   │   ├── test_group_service.py
│   │   └── test_timetable_parser.py
│   ├── integration/
│   │   ├── test_auth_api.py
│   │   ├── test_friends_api.py
│   │   ├── test_groups_api.py
│   │   ├── test_availability_api.py
│   │   └── test_timetable_import.py
│   └── fixtures/
│       ├── users.py
│       ├── timetables.py                # Sample Excel mock data
│       └── db.py
│
├── requirements.txt                     # Or pyproject.toml
├── Dockerfile
├── .env.example
└── docker-compose.yml
```

### Module Boundary Rules

| File | Contains | Must NOT contain |
|------|----------|------------------|
| `repositories/*.py` | SQLAlchemy queries, raw SQL | Business logic, type coercion, HTTP concepts |
| `services/*.py` | Business rules, orchestration | HTTP request/response objects, SQL |  
| `api/v1/*.py` | Route handlers, HTTP decorators | Business logic, SQL queries |
| `schemas/*/requests.py` | Request Pydantic models | Response formatting |
| `schemas/*/responses.py` | Response Pydantic models | Validation logic beyond types |
| `models/*.py` | ORM column definitions, relationships, table args | Serialization logic, business methods |

---

## 3. Layer Architecture

### Request Flow

```
                         ┌──────────┐
                         │  Client  │
                         └────┬─────┘
                              │ HTTP
                              ▼
                     ┌─────────────────┐
                     │   Middleware     │
                     │ • CORS          │
                     │ • Request ID    │
                     │ • Rate Limit    │
                     │ • Log context   │
                     └────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   API Router     │
                    │ (route handler)  │
                    │                  │
                    │ 1. Extract path  │
                    │    params        │
                    │ 2. Validate body │
                    │    (Pydantic)    │
                    │ 3. Call service  │
                    │ 4. Format        │
                    │    response      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Service       │
                    │                  │
                    │ 1. Business      │
                    │    rules         │
                    │ 2. Orchestration │
                    │ 3. Call repos    │
                    │ 4. Raise domain  │
                    │    exceptions    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Repository     │
                    │                  │
                    │ 1. Build query   │
                    │ 2. Execute       │
                    │ 3. Map → model   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Database /     │
                    │   Cache          │
                    └──────────────────┘
```

### Layer Communication

```python
# Layer boundaries expressed as type constraints

# API Layer — only uses request/response schemas
from app.schemas.auth.requests import RegisterRequest
from app.schemas.auth.responses import TokenResponse

@router.post("/auth/register", status_code=201)
async def register(
    body: RegisterRequest,                          # Pydantic validated
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    result = await auth_service.register(            # Service returns domain result
        roll_number=body.roll_number,
        device_fingerprint=body.device_fingerprint,
        device_name=body.device_name,
    )
    return TokenResponse.from_domain(result)         # Response schema assembles output


# Service Layer — uses internal schemas for data transfer
from app.schemas.auth.internal import RegistrationResult
from app.repositories.user_repository import UserRepository
from app.repositories.device_repository import DeviceRepository

class AuthService:
    def __init__(self, user_repo: UserRepository, device_repo: DeviceRepository):
        self.user_repo = user_repo
        self.device_repo = device_repo

    async def register(
        self, roll_number: str, device_fingerprint: str, device_name: str | None
    ) -> RegistrationResult:
        existing = await self.user_repo.find_by_roll_number(roll_number)
        if existing:
            raise UserAlreadyExistsError()
        user = await self.user_repo.create(roll_number=roll_number)
        device = await self.device_repo.create(
            user_id=user.id,
            fingerprint=device_fingerprint,
            name=device_name,
        )
        tokens = generate_tokens(user.id, device.id)
        return RegistrationResult(user=user, device=device, tokens=tokens)


# Repository Layer — returns ORM models or raw dicts
class UserRepository(BaseRepository[User]):
    async def find_by_roll_number(self, roll_number: str) -> User | None:
        stmt = select(User).where(User.roll_number == roll_number)
        return await self.session.scalar(stmt)
```

---

## 4. Database Layer

### Engine & Session Factory

```python
# app/core/database.py

# Single async engine, shared across the application
# Connection pool: 20-100 connections, configurable via settings
# Pool recycling every 300s to prevent stale connections
# Prepared statements enabled

async_engine = create_async_engine(
    url=settings.database.url,           # postgresql+asyncpg://...
    pool_size=settings.database.pool_size,       # 20
    max_overflow=settings.database.max_overflow,  # 80 (peak total: 100)
    pool_recycle=300,
    pool_pre_ping=True,
    echo=settings.debug,                  # SQL logging only in dev
    json_serializer=orjson.dumps,
    json_deserializer=orjson.loads,
)

async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
```

### Base Model

```python
# app/models/base.py

class TimestampMixin:
    created_at: datetime = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: datetime = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class Base(DeclarativeBase, TimestampMixin):
    # All models inherit from this
    # Provides: id (UUID PK), created_at, updated_at
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid7,                     # Time-ordered UUID v7 for index perf
        nullable=False,
    )
```

### Index Strategy

```python
# Index naming convention:
#   idx_{table}_{column(s)} — for single/multi-column performance indexes
#   uq_{table}_{column(s)}  — for unique constraints
#   ix_{table}_{column}     — for full-text search indexes

# Timetable lookup — the hottest query path
__table_args__ = (
    Index("idx_tt_section_day", "section_id", "day_of_week"),
    # Composite index for: "find all classes for section X on day Y"
    # Also covers: "find section X's schedule for today"
)

# Friend lookup — bidirectional, needs both directions
__table_args__ = (
    Index("idx_friends_user", "user_id"),
    Index("idx_friends_friend", "friend_id"),
)
```

### Connection Management

```python
# Dependency: one session per request, auto-committed on success
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## 5. Repository Layer

### Base Repository

```python
# app/repositories/base.py

class BaseRepository[T: Base]:
    """Abstract CRUD with common operations.

    Every repository extends this. Provides:
    - get(id) -> T | None
    - get_or_raise(id) -> T (raises NotFoundError)
    - list(*filters) -> list[T]
    - create(**data) -> T
    - update(id, **data) -> T
    - delete(id) -> None
    - exists(**filters) -> bool
    - count(**filters) -> int
    """

    model_class: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> T | None: ...
    async def get_or_raise(self, id: UUID) -> T:
        instance = await self.get(id)
        if not instance:
            raise NotFoundError(self.model_class.__name__, id)
        return instance
    async def list(self, *whereclause, limit: int = 100, offset: int = 0) -> list[T]: ...
    async def create(self, **data) -> T: ...
    async def update(self, id: UUID, **data) -> T: ...
    async def delete(self, id: UUID) -> None: ...
    async def exists(self, **filters) -> bool: ...
    async def count(self, **filters) -> int: ...
```

### Repository Contract Example

```python
# app/repositories/timetable_entry_repository.py

class TimetableEntryRepository(BaseRepository[TimetableEntry]):
    """Data access for timetable entries.

    Key queries:
    - get_by_section(section_id, day) — all entries for a section on a given day
    - get_by_sections(section_ids, day) — batch for group comparison
    - get_current_class(section_id) — currently active class
    - get_next_event(section_id, after) — next class after a timestamp
    """

    async def get_by_section(
        self, section_id: UUID, day_of_week: int | None = None
    ) -> list[TimetableEntry]:
        """Fetch all timetable entries for a section, optionally filtered by day."""

    async def get_by_sections(
        self, section_ids: list[UUID], day_of_week: int
    ) -> dict[UUID, list[TimetableEntry]]:
        """Batch fetch — one query for N sections. Returns dict keyed by section_id."""
```

### Repository Design Rules

1. **One repository per aggregate root.** Friend, FriendRequest, and FriendBlock all live in `FriendRepository` because they form one aggregate.

2. **Repositories return ORM models or primitives.** Never return Pydantic schemas. The service layer handles the mapping.

3. **Repositories never catch domain exceptions.** They re-raise integrity errors from the DB as database-level exceptions. The service layer translates them to domain exceptions.

4. **Batch operations return dicts, not lists.** When fetching data for multiple parents (e.g., timetable entries for N sections), return `dict[parent_id, list[child]]` so the service can do O(1) lookups.

5. **Repositories are not cached.** Caching is a service concern. A repository asks "what does the database have?" and a service asks "do I have it cached, or should I ask the repository?"

---

## 6. Service Layer

### Service Contract Example

```python
# app/services/availability_service.py

class AvailabilityService:
    """Core business logic for availability computation.

    This is the most critical service in the application.
    All methods are read-only (no mutations).
    Cache-friendly — results can be cached by day/section combo.

    Responsibilities:
    - Compute individual availability at a point in time
    - Compute common free slots for a set of users
    - Determine connection state for constellation visualization
    - Answer: "who is free right now among my friends?"
    """

    def __init__(
        self,
        user_repo: UserRepository,
        timetable_entry_repo: TimetableEntryRepository,
        friend_repo: FriendRepository,
        group_member_repo: GroupMemberRepository,
        cache: CacheService,
    ):
        ...

    async def get_status(
        self, user_id: UUID, at: datetime | None = None
    ) -> UserStatus:
        """Free, in_class, or away. Returns current class details if busy."""

    async def get_schedule(
        self, user_id: UUID, date: date
    ) -> Schedule:
        """Full day schedule: busy slots + free slots."""

    async def compare_with_friend(
        self, user_id: UUID, friend_id: UUID, date: date
    ) -> ComparisonResult:
        """Common free slots, next common slot, both_free_now."""

    async def compare_batch(
        self, user_id: UUID, friend_ids: list[UUID], date: date
    ) -> dict[UUID, FriendAvailability]:
        """Batch friend comparison for dashboard."""

    async def get_group_overlap(
        self, group_id: UUID, date: date
    ) -> GroupOverlap:
        """Aggregate availability for all group members."""

    async def get_constellation_state(
        self, group_id: UUID
    ) -> ConstellationState:
        """Current live state: which members are free, connection map."""

    async def next_common_slot(
        self, user_ids: list[UUID], after: datetime
    ) -> TimeSlot | None:
        """Next time all given users are simultaneously free."""

    async def longest_common_slot(
        self, user_ids: list[UUID], date: date
    ) -> TimeSlot | None:
        """Longest continuous block where all users are free."""
```

### Service Design Rules

1. **Services receive primitives, not request objects.** No `Request` objects enter a service. This keeps services HTTP-agnostic and testable.

2. **Services raise domain exceptions.** `UserNotFoundError`, `FriendAlreadyExistsError`, `NotGroupMemberError`. These are caught by global error handlers and mapped to HTTP responses.

3. **Services call repositories and other services.** They orchestrate. They do not contain SQL or HTTP logic.

4. **Services handle caching.** Before calling a repository, check the cache. After writing, invalidate the relevant cache keys. The cache interface is injected like any other dependency.

5. **Services are stateless singletons.** One instance per request. All state comes from arguments or repositories. This makes them thread-safe and easy to reason about.

6. **Complex queries use internal Pydantic models.** If a service needs to return a data structure that spans multiple database tables, define an internal schema in `schemas/*/internal.py`. The service returns this model; the API layer maps it to the response schema.

### Service Interaction — Availability Flow

```
get_group_overlap(group_id, date)
    │
    ├── group_member_repo.get_members(group_id)
    │   Returns: list[GroupMember]
    │
    ├── For each member → get their section_id
    │   user_repo.get_section_ids(member_ids)
    │   Returns: dict[UUID, UUID]  (user_id → section_id)
    │
    ├── timetable_entry_repo.get_by_sections(section_ids, day_of_week)
    │   Returns: dict[UUID, list[TimetableEntry]]  (section_id → entries)
    │
    ├── For each member → compute free slots
    │   time_utils.busy_to_free(entries, bounds=(08:00, 20:00))
    │   Returns: dict[UUID, list[TimeRange]]  (user_id → free slots)
    │
    └── time_utils.intersect_all(free_slots_by_user)
        Returns: list[TimeRange]  (common free slots)
```

---

## 7. API Layer

### Router Structure

```python
# app/api/v1/router.py

api_v1_router = APIRouter(prefix="/api/v1")

# No business logic in route files — only:
# 1. Path/query parameter extraction
# 2. Body validation via Pydantic
# 3. Service injection via Depends
# 4. Response formatting + status codes

api_v1_router.include_router(auth.router,    prefix="/auth",    tags=["Authentication"])
api_v1_router.include_router(users.router,   prefix="/users",   tags=["Users"])
api_v1_router.include_router(friends.router, prefix="/friends", tags=["Friends"])
api_v1_router.include_router(groups.router,  prefix="/groups",  tags=["Groups"])
api_v1_router.include_router(availability.router, prefix="/availability", tags=["Availability"])
api_v1_router.include_router(timetables.router, prefix="/timetables", tags=["Timetables"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(admin.router,   prefix="/admin",   tags=["Admin"])
```

### Route Handler Contract

```python
# app/api/v1/groups.py

@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group_detail(
    group_id: UUID = Path(..., description="Group UUID"),
    current_user: User = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service),
    availability_service: AvailabilityService = Depends(get_availability_service),
) -> GroupDetailResponse:
    # 1. Authorization check (service raises if not member)
    group = await group_service.get_group(group_id, current_user.id)

    # 2. Business logic delegated to services
    members = await group_service.get_members(group_id)
    constellation = await availability_service.get_constellation_state(group_id)

    # 3. Response assembly (no formatting logic in handler)
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        members=[MemberResponse.from_domain(m) for m in members],
        constellation=ConstellationStateResponse.from_domain(constellation),
    )
```

### API Response Conventions

| Aspect | Convention |
|--------|-----------|
| Success | `return response_schema.from_domain(service_result)` |
| Creation | `status_code=201`, `return response_schema.from_domain(created)` |
| Deletion | `status_code=204`, no body |
| Background task | `status_code=202`, `return {"task_id": str, "status": "processing"}` |
| Validation error | Pydantic `ValidationError` → 422 via FastAPI handler |
| Business error | Domain exception → global exception handler → 4xx JSON |
| Unexpected error | 500 via global handler, logged with trace ID |

---

## 8. Pydantic Schemas

### Schema Organization

```
schemas/
├── common.py                      # Shared types across all modules
├── auth/
│   ├── requests.py                # RegisterRequest, RefreshRequest, LogoutRequest
│   ├── responses.py               # TokenResponse, UserWithTokenResponse
│   └── internal.py                # DeviceInfo (DTO between service + repo)
├── users/
│   ├── requests.py                # UpdateProfileRequest, SearchQuery
│   ├── responses.py               # UserResponse, UserSearchResponse
│   └── internal.py                # UserWithSection (joined data)
├── friends/
│   ├── requests.py                # AddFriendRequest
│   ├── responses.py               # FriendResponse, FriendStatusResponse
│   └── internal.py                # FriendWithUser (joined data)
├── groups/
│   ├── requests.py                # CreateGroupRequest, UpdateGroupRequest, AddMembersRequest
│   ├── responses.py               # GroupResponse, GroupDetailResponse, MemberResponse
│   └── internal.py                # GroupWithMemberCount
├── availability/
│   ├── requests.py                # CompareQuery, DateQuery
│   ├── responses.py               # UserStatusResponse, ScheduleResponse,
│   │                              # ComparisonResponse, GroupOverlapResponse,
│   │                              # ConstellationStateResponse
│   └── internal.py                # UserStatus, TimeSlot, BusyRange, FreeRange
├── timetables/
│   ├── requests.py                # ImportQuery (for admin filtering)
│   ├── responses.py               # ImportStatusResponse, ImportProgressResponse
│   └── internal.py                # ParsedRow, NormalizedEntry
├── notifications/
│   └── responses.py               # NotificationResponse, NotificationListResponse
└── realtime/
    └── events.py                  # AvailabilityUpdate, ConstellationUpdate,
                                   # FriendStatusChange, Ping, Pong, Error
```

### Internal Schema Example

```python
# schemas/availability/internal.py

class TimeSlot(BaseModel):
    """A time range with start and end. Used for slot intersection."""
    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)

class UserStatus(BaseModel):
    """Current availability status of a user at a point in time."""
    user_id: UUID
    status: Literal["free", "in_class", "away"]
    current_class: ClassInfo | None = None
    since: datetime                           # When this status started
    next_event: ClassInfo | None = None       # Next class or end of free

class BusyRange(BaseModel):
    """A busy time range with course details."""
    start: datetime
    end: datetime
    course_code: str
    course_name: str
    venue: str
    slot_type: str

class GroupOverlap(BaseModel):
    """Aggregated availability for all group members."""
    group_id: UUID
    date: date
    common_slots: list[TimeSlot]
    next_slot: TimeSlot | None
    longest_slot: TimeSlot | None
    free_now_count: int
    total_count: int
```

### Schema Design Rules

1. **Request schemas validate input strictly.** Use Pydantic validators for format checks (e.g., `roll_number` pattern `^\d{4}[A-Z]{3}\d{4}$`). Return informative error messages.

2. **Response schemas define the API contract.** Exactly what the client receives. No extra fields. Use `json_schema_extra=Example` for OpenAPI documentation.

3. **Internal schemas bridge services and repositories.** They exist to avoid leaking ORM models outside the repository layer. A service receives internal schemas from repositories and passes them to other services or to the API layer.

4. **Schema conversion is explicit.** Each response schema has a `from_domain` classmethod that maps from internal/ORM models. This keeps serialization logic in the schema, not in the route handler.

5. **No model nesting in request schemas.** Flatten request bodies. The service layer is responsible for assembling nested domain objects.

---

## 9. Dependency Injection

### FastAPI Dependencies

```python
# app/api/deps.py — shared dependencies

# Database session
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...

# Current authenticated user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User: ...

# Current user with admin check
async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise InsufficientPermissionsError()
    return user

# Service factories
def get_auth_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_cache),
) -> AuthService:
    user_repo = UserRepository(db)
    device_repo = DeviceRepository(db)
    return AuthService(
        user_repo=user_repo,
        device_repo=device_repo,
        cache=cache,
    )

def get_availability_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_cache),
) -> AvailabilityService:
    user_repo = UserRepository(db)
    tt_entry_repo = TimetableEntryRepository(db)
    friend_repo = FriendRepository(db)
    group_member_repo = GroupMemberRepository(db)
    cache_service = CacheService(cache)
    return AvailabilityService(
        user_repo=user_repo,
        tt_entry_repo=tt_entry_repo,
        friend_repo=friend_repo,
        group_member_repo=group_member_repo,
        cache=cache_service,
    )
```

### DI Rules

1. **Repositories are instantiated per request.** They hold a reference to the session. Sessions are request-scoped.

2. **Services are instantiated per request.** They receive repository instances. This keeps the dependency graph explicit and makes testing easy (override `Depends` with mock services).

3. **No global singletons.** No `from app.services.foo import foo_service`. Everything is injected. This prevents hidden dependencies and makes request tracing possible.

4. **Circular dependencies are a design smell.** If service A needs service B and B needs A, extract the shared logic into a third service or a utility module.

---

## 10. Middleware Stack

### Middleware Order

```python
# app/main.py — middleware registration order matters

def create_app() -> FastAPI:
    app = FastAPI(
        title="Constellation API",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
    )

    # 1. Request ID — earliest, captures trace ID
    app.add_middleware(RequestIDMiddleware)

    # 2. CORS — before auth, preflight requests
    app.add_middleware(CORSMiddleware, ...)

    # 3. Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # 4. Log context — after request ID, before business logic
    app.add_middleware(LogContextMiddleware)

    # 5. Rate limiting — after auth (uses user_id if available)
    app.add_middleware(RateLimitMiddleware)

    # 6. Process time — measures and logs request duration
    app.add_middleware(ProcessTimeMiddleware)

    # Register routers
    app.include_router(api_v1_router)

    # Register exception handlers
    register_error_handlers(app)

    # Register startup/shutdown events
    @app.on_event("startup")
    async def startup():
        await connect_redis()
        await verify_database_connection()

    @app.on_event("shutdown")
    async def shutdown():
        await disconnect_redis()
        await dispose_database_engine()

    return app
```

### Middleware Specifications

```python
# 1. RequestIDMiddleware — every request gets a unique trace ID
#   - Generate UUID v7
#   - Set on request.state.request_id
#   - Add to response header: X-Request-ID

# 2. CORSMiddleware — restrict to frontend origin
#   - allow_origins = [settings.frontend_url]  # exact, not wildcard
#   - allow_credentials = True
#   - allow_methods = ["GET", "POST", "PATCH", "DELETE"]
#   - allow_headers = ["Authorization", "Content-Type"]

# 3. SecurityHeadersMiddleware
#   - X-Content-Type-Options: nosniff
#   - X-Frame-Options: DENY
#   - Content-Security-Policy: default-src 'none'
#   - Referrer-Policy: strict-origin-when-cross-origin
#   - Permissions-Policy: geolocation=(), microphone=(), camera=()

# 4. LogContextMiddleware
#   - Inject request_id, user_id (if authenticated), method, path into logging context
#   - Structured log fields for log aggregation (Datadog, Grafana Loki)

# 5. RateLimitMiddleware
#   - Uses Redis as the rate limiter store
#   - Sliding window algorithm
#   - Per-IP for unauthenticated endpoints (5/min for register)
#   - Per-user for authenticated endpoints (100/min general, 30/min for search)
#   - Returns 429 with Retry-After header
#   - Critical: auth endpoints have the strictest limits

# 6. ProcessTimeMiddleware
#   - Record start time in request.state
#   - On response, calculate duration
#   - Add X-Process-Time header (ms)
#   - Log slow requests (>500ms) as warnings with full trace
```

---

## 11. Authentication System

### Design Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AUTHENTICATION SYSTEM                         │
│                                                                     │
│  Passwordless. Device-bound. Token-rotating.                        │
│                                                                     │
│  ┌───────────┐    ┌──────────┐    ┌──────────────┐                  │
│  │ Register  │───→│  Verify  │───→│ Issue Tokens │                  │
│  └───────────┘    └──────────┘    └──────┬───────┘                  │
│                                          │                          │
│                    ┌─────────────────────┼──────────────┐           │
│                    ▼                     ▼              ▼           │
│             ┌───────────┐        ┌────────────┐  ┌──────────┐      │
│             │ JWT       │        │ Refresh    │  │ Device   │      │
│             │ (15 min)  │        │ (30 days)  │  │ Binding  │      │
│             └───────────┘        └────────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```python
# app/services/auth_service.py

class AuthService:
    """Handles registration, token lifecycle, and device management.

    Security guarantees:
    - No passwords stored anywhere
    - Device fingerprint is SHA-256 hashed with app salt
    - Refresh tokens are bcrypt hashed at rest
    - Token rotation: each refresh invalidates the previous token
    - One device per session (registering a new device logs out the old one)
    - Account enumeration prevented (same response time for found/not-found)
    """

    async def register(
        self,
        roll_number: str,
        device_fingerprint: str,
        device_name: str | None,
    ) -> RegistrationResult:
        """
        1. Check if roll_number exists → create user or return existing
           (Same timing for both paths to prevent enumeration)
        2. Hash the device fingerprint (SHA-256 + salt)
        3. Check if this device is already registered → rotate or create
        4. If "one active device" policy:
           - Deactivate all existing devices for this user
           - OR: only if the new device_fingerprint differs
        5. Generate JWT (15 min) + Refresh token (random 128-bit)
        6. Store bcrypt hash of refresh token + device fingerprint
        7. Return tokens + user info
        """

    async def refresh(
        self,
        refresh_token: str,
        device_fingerprint: str,
    ) -> TokenRefreshResult:
        """
        1. Hash device_fingerprint → lookup device
        2. Verify bcrypt(refresh_token) matches stored hash
        3. If mismatch → log security event, return 401
        4. Generate new JWT + rotate refresh token
        5. Update stored refresh token hash
        6. Return new tokens
        7. Old refresh token is now invalid (rotation)
        """

    async def logout(self, user_id: UUID, device_id: UUID) -> None:
        """
        1. Delete device record
        2. All JWTs issued to this device are now invalid
           (They will fail the user_id + device_id check)
        """

    async def revoke_all_devices(self, user_id: UUID) -> None:
        """
        1. Delete ALL device records for user
        2. Admin-only action (compromised account recovery)
        """
```

### Token Design

```python
# JWT Structure
# Header:  { "alg": "HS256", "typ": "JWT" }
# Payload: {
#     "sub": "uuid-of-user",        # User ID
#     "did": "uuid-of-device",      # Device ID (binding)
#     "iat": 1700000000,            # Issued at
#     "exp": 1700000900,            # Expires (15 min)
#     "jti": "uuid-v4",            # Unique token ID (revocation list support)
# }
# Signing: HMAC-SHA256 with APP_SECRET

# Refresh Token Structure (not JWT)
# Random 128-bit UUID v4 → 36 character string
# Stored as bcrypt hash (cost=10) in devices.refresh_token_hash
# Rotated on every use

# Security properties:
# - JWT expiry: 15 minutes (minimizes blast radius of token theft)
# - Refresh token expiry: 30 days since last_used_at
# - Device binding: both JWT (did claim) and refresh (device_fingerprint parameter)
# - Token rotation: old refresh token invalid after successful refresh
# - On device change: old device's tokens remain valid until expiry (unless revoked)
```

### Anti-Abuse Measures

```python
# Account enumeration prevention
async def register(self, roll_number: str, ...) -> RegistrationResult:
    # Use constant-time comparison for roll_number lookup
    # Same error message regardless of whether user exists:
    # "If this roll number is valid, a verification code was sent"
    # (OTP is future; for MVP, just return tokens)

    # Simulate DB query delay on both paths to prevent timing attacks
    user = await self.user_repo.find_by_roll_number(roll_number)
    if not user:
        # Artificial delay: ~50ms to match the "found" path
        await asyncio.sleep(settings.auth.ENUMERATION_PREVENTION_DELAY)
        # Create the user
        user = await self.user_repo.create(roll_number=roll_number)
    # Continue with device registration...

# Brute force prevention
# Rate limits on /auth routes: 5 requests/min per IP
# Rate limits on /auth/refresh: 10 requests/min per device
# After 10 consecutive failed refresh attempts: lock device for 15 min

# Scraping prevention
# User search: requires auth, returns minimal info (no sections, no availability)
# Search results: max 10 results, no pagination beyond page 1 for unauthenticated
# Roll number never exposed in public responses (use UUID display_name instead)

# API abuse detection
# Monitor: rapid friend adds, rapid group creates, rapid availability checks
# If pattern detected: escalate to admin alert + temporary IP block
```

### UUID Internal Identity

```python
# Roll numbers are never exposed via API responses
# All public identifiers are UUIDs

# UserResponse:
# {
#     "id": "550e8400-e29b-41d4-a716-446655440000",  # UUID (public)
#     "display_name": "Alice",                        # Derived from roll number
#     "section": { ... },
# }
# NEVER: { "roll_number": "2021CSB1078" }  # This is internal only

# Friend search
# GET /users/search?q=2021CSB
# Response: [{ "id": "uuid", "display_name": "Alice" }]
# NEVER return roll_number in search results
```

---

## 12. Timetable Engine

### Architecture

```
                    ┌──────────────────┐
                    │  Excel Workbook  │   .xlsx file
                    └────────┬─────────┘
                             │ (upload via admin)
                             ▼
                    ┌──────────────────┐
                    │  Parser Service  │   Background task
                    │  (thread pool)   │
                    └────────┬─────────┘
                             │ Raw rows
                             ▼
                    ┌──────────────────┐
                    │ Normalization    │   Dedup, validate, type-coerce
                    │ Service          │
                    └────────┬─────────┘
                             │ Normalized records
                             ▼
                    ┌──────────────────┐
                    │ Import Service   │   Orchestrator
                    │                  │
                    │ 1. Validate      │
                    │ 2. Create/update │
                    │    sections      │
                    │ 3. Create/update │
                    │    courses       │
                    │ 4. Create/update │
                    │    timeslots     │
                    │ 5. Bulk insert   │
                    │    tt_entries    │
                    │ 6. Verify counts │
                    └────────┬─────────┘
                             │ Transactional
                             ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    └──────────────────┘
                             ▲
                    ┌────────┴─────────┐
                    │ Query Service    │   Read-only, used during normal requests
                    │ (section lookup) │
                    └──────────────────┘
```

### Parser Service

```python
# app/services/timetable_parser_service.py

class TimetableParserService:
    """Parses the Excel workbook into raw, unvalidated records.

    Runs in a thread pool executor (CPU-bound: openpyxl).
    Output is a list of ParsedRow objects — one per cell intersection.

    Responsibilities:
    - Open workbook via openpyxl
    - Iterate sheets
    - Extract: department, section, course code, course name,
               day, start time, end time, venue, slot type
    - Return list[ParsedRow] (raw, unvalidated)
    - Handle: merged cells, header rows, empty rows, inconsistent formats

    Non-responsibilities:
    - Validation (delegated to Normalization Service)
    - Database operations (delegated to Import Service)

    Error handling:
    - On first structural error (can't parse sheet layout), raise immediately
    - On data errors (invalid time format), collect all errors, return with results
    - No partial workbook state — everything is in memory
    """

    async def parse(self, file_path: str) -> ParseResult:
        # Runs in thread pool executor to avoid blocking the event loop
        # Returns: ParseResult(raw_rows=[...], errors=[...])
```

### Normalization Service

```python
# app/services/timetable_normalization_service.py (or within parser)

class TimetableNormalizationService:
    """Validates and normalizes parsed rows.

    Responsibilities:
    - Strip whitespace from all string fields
    - Validate roll number patterns
    - Validate time formats (HH:MM)
    - Validate day names → day_of_week (0-6)
    - Validate slot_type against allowed values
    - Deduplicate: identical (section, course, day, start, end)
    - Return NormalizedRows with stable field types
    - Collect all validation errors (don't fail on first error)

    Output is deterministic: same workbook → same NormalizedRows.
    """

    async def normalize(self, raw_rows: list[ParsedRow]) -> NormalizationResult:
        # Returns: NormalizationResult(rows=[...], errors=[...])
```

### Import Service

```python
# app/services/timetable_import_service.py

class TimetableImportService:
    """Orchestrates the full import pipeline.

    1. Accept file path
    2. Call ParserService.parse()
    3. Call NormalizationService.normalize()
    4. If errors → return errors, no DB changes
    5. Open transaction
    6. Upsert sections (match by name + dept + semester + year)
    7. Upsert courses (match by code + department)
    8. Upsert timeslots (match by day + start + end)
    9. Bulk insert timetable_entries (delete old, insert new for each section)
    10. Verify counts match expected
    11. Commit transaction
    12. Invalidate all availability caches (clear entire cache namespace)
    13. Return ImportResult with counts

    Transaction behavior:
    - All-or-nothing: if any step fails, entire import is rolled back
    - Previous timetable is NOT affected until new one is fully committed
    - On success, old data is replaced atomically (DELETE + INSERT in same TX)

    Caching:
    - After successful import, flush ALL availability cache keys
    - Previous cached data is stale; next availability query must see new data
    """

    async def import_workbook(
        self, file_path: str, imported_by: UUID
    ) -> ImportResult:
        ...
```

### Query Service

```python
# app/services/timetable_query_service.py

class TimetableQueryService:
    """Read-only timetable lookups.

    This is the ONLY timetable service used during normal user requests.
    The workbook is never touched. Data comes exclusively from PostgreSQL.

    Caching strategy:
    - Results are cached by (section_id, day_of_week)
    - Cache TTL: 5 minutes (timetable is static for the semester)
    - Cache is invalidated on import

    Key methods:
    - get_section_schedule(section_id, day) -> list[TimeSlot]
    - get_section_schedules(section_ids, day) -> dict[section_id, list[TimeSlot]]
    - get_current_class(section_id, at) -> TimeSlot | None
    - get_next_class(section_id, after) -> TimeSlot | None
    - get_daily_busy_slots(section_id, date) -> list[TimeSlot]

    All methods delegate to TimetableEntryRepository.
    All results are cached.
    """
```

---

## 13. Availability Engine

### Architecture

```
                    ┌─────────────────────────────────────┐
                    │         AvailabilityService         │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │     Individual Status         │  │
                    │  │  get_status(user_id, at)      │  │
                    │  │  get_schedule(user_id, date)  │  │
                    │  └───────────────────────────────┘  │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │     Friend Comparison         │  │
                    │  │  compare_with_friend(uid, fid)│  │
                    │  │  compare_batch(uid, f_ids)    │  │
                    │  └───────────────────────────────┘  │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │     Group Overlap             │  │
                    │  │  get_group_overlap(gid, date) │  │
                    │  │  get_constellation_state(gid) │  │
                    │  │  next_common_slot(u_ids, at)  │  │
                    │  │  longest_common_slot(u_ids, d)│  │
                    │  └───────────────────────────────┘  │
                    └──────────┬──────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
  ┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │  UserRepo     │  │ TimetableEntry   │  │  FriendRepo /    │
  │  (section_id) │  │ Repo (schedule)  │  │  GroupMemberRepo │
  └───────────────┘  └──────────────────┘  └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Time Utils     │
                    │  (slot math)     │
                    └──────────────────┘
```

### Core Algorithm — Slot Intersection

```python
# app/utils/time_utils.py

# All availability logic reduces to three primitive operations:

def get_free_slots(
    busy_slots: list[TimeSlot],
    day_start: datetime = 08:00,
    day_end: datetime = 20:00,
) -> list[TimeSlot]:
    """
    Given a list of busy slots, compute free time ranges.

    1. Sort busy slots by start time
    2. Merge overlapping/adjacent busy slots
    3. Invert: gaps between busy slots are free slots
    4. Bound by [day_start, day_end]
    5. Filter out slots shorter than 5 minutes

    Returns: sorted list of free TimeSlots
    """

def intersect_many(
    free_slots_by_user: dict[UUID, list[TimeSlot]],
) -> list[TimeSlot]:
    """
    Given per-user free slot lists, find common free slots.

    1. Take first user's free slots as the candidate set
    2. For each subsequent user, intersect candidate set with their free slots
    3. Intersection: [max(start_a, start_b), min(end_a, end_b)]
    4. Keep only intersections with duration >= 5 minutes

    Returns: sorted list of common TimeSlots
    """

def find_next_common_slot(
    free_slots_by_user: dict[UUID, list[TimeSlot]],
    after: datetime,
) -> TimeSlot | None:
    """
    Next time all users are free.

    1. Common slots = intersect_many(free_slots_by_user)
    2. Filter: start >= after
    3. Return first (earliest) or None
    """

def find_longest_common_slot(
    free_slots_by_user: dict[UUID, list[TimeSlot]],
) -> TimeSlot | None:
    """
    Longest continuous block of common free time.

    1. Common slots = intersect_many(free_slots_by_user)
    2. Sort by duration descending
    3. Return first (longest) or None
    """
```

### Constellation State Computation

```python
class AvailabilityService:
    async def get_constellation_state(
        self, group_id: UUID
    ) -> ConstellationState:
        """
        Compute the live constellation state for a group.

        Algorithm:
        1. Get all members of the group
        2. For each member, get their current status (free/busy/away/offline)
        3. Count free members
        4. Generate connection map:
           - If both users are free → they are connected
           - If exactly 2 free → single connection
           - If 3+ free → connect adjacent members in layout order
           - If all free → connect everyone (complete graph)
        5. Set is_all_free = (free_count == total_count)

        Returns:
            ConstellationState(
                members=[{id, name, status, status_since}],
                connections=[(user_a_id, user_b_id), ...],
                free_count=N,
                total_count=N,
                is_all_free=True/False,
            )
        """

    async def get_constellation_state_batch(
        self, group_ids: list[UUID]
    ) -> dict[UUID, ConstellationState]:
        """
        Batch version for the dashboard group list.
        Single query for all groups, single query for all memberships.
        O(G + M) instead of O(G * M).
        """
```

### Performance Characteristics

| Operation | DB Queries | Cache Keys | Complexity |
|-----------|-----------|------------|------------|
| Single status (me) | 1 | 1 get + 1 set | O(1) |
| Single schedule (me) | 1 | 1 get + 1 set | O(E) where E = entries |
| Friend comparison | 2 | 2 get + 2 set | O(E1 + E2) |
| Batch friend list | 1 + N | N get + N set | O(N * E_avg) — mitigated by batch query |
| Group overlap | 1 + N | 1 get + 1 set | O(N * E_avg) |
| Constellation state | 1 + N | N get + N set | O(N) — status check only |
| Next common slot | 1 + N | N get | O(N * E_avg) |
| Longest common slot | 1 + N | N get | O(N * E_avg) |

Where N = members/friends, E = timetable entries per section (≈8 max)

### Future Realtime Integration

```python
# The AvailabilityService is designed to be wrapped by the RealtimeService:

class RealtimeService:
    """Wraps AvailabilityService with WebSocket push.

    On status change detection (polling or event-driven):
    1. Compute new constellation state for affected groups
    2. Check what changed (which members flipped free/busy)
    3. Build push payload with only the delta
    4. Broadcast to subscribed WebSocket clients

    Status change detection strategies:
    - Polling: scheduler checks every 60s for scheduled transitions
    - Event-driven: timetable import triggers full cache flush
    - Future: listen to PostgreSQL LISTEN/NOTIFY for realtime events
    """

    async def on_availability_change(
        self, affected_user_ids: list[UUID]
    ) -> None:
        # 1. Find all groups containing these users
        group_ids = await self.group_member_repo.get_group_ids_for_users(
            affected_user_ids
        )
        # 2. Fetch new constellation states for all affected groups
        states = await self.availability_service.get_constellation_state_batch(
            group_ids
        )
        # 3. Push to WebSocket subscribers
        for group_id, state in states.items():
            message = ConstellationUpdate(
                group_id=group_id,
                constellation=state,
                delta=self._compute_delta(group_id, state),
            )
            await self.ws_manager.broadcast(f"group:{group_id}", message)
```

---

## 14. Caching Architecture

### Cache Key Design

```python
# app/core/cache.py

# All cache keys follow a consistent namespace pattern:
# {prefix}:{entity_type}:{identifier}:{modifier}

CACHE_KEYS = {
    # Auth — short TTL, sensitive
    "device_lock":       "auth:device:{device_fingerprint}:lock",        # 15 min
    "refresh_lock":      "auth:refresh:{user_id}:count",                # 1 min

    # User — medium TTL, rarely changes
    "user":              "user:{user_id}",                               # 5 min
    "user_section":      "user:{user_id}:section",                       # 5 min
    "user_search":       "user:search:{query_hash}",                     # 1 min

    # Friends — short TTL (friend list can change)
    "friends":           "friends:{user_id}",                            # 30s
    "friend_ids":        "friends:{user_id}:ids",                        # 30s

    # Groups — medium TTL
    "group":             "group:{group_id}",                             # 5 min
    "group_members":     "group:{group_id}:members",                     # 5 min
    "user_groups":       "user:{user_id}:groups",                        # 5 min

    # Timetable — long TTL (static data)
    "section_schedule":  "tt:section:{section_id}:day:{day_of_week}",    # 1 hour
    "section_schedules": "tt:section:{section_id}:schedule",            # 1 hour

    # Availability — short TTL (changes on class boundaries)
    "user_status":       "avail:user:{user_id}:status",                 # 30s
    "user_schedule":     "avail:user:{user_id}:schedule:{date}",        # 5 min
    "friend_comparison": "avail:compare:{user_id}:{friend_id}:{date}",  # 1 min
    "group_overlap":     "avail:group:{group_id}:{date}",               # 1 min
    "constellation":     "avail:constellation:{group_id}",              # 30s

    # Rate limiting
    "rate_limit_ip":     "ratelimit:ip:{ip}:{endpoint}",                # 1 min
    "rate_limit_user":   "ratelimit:user:{user_id}:{endpoint}",         # 1 min

    # Import lock
    "import_lock":       "import:lock",                                  # 5 min
}
```

### Cache Invalidation Matrix

| Event | Cache Keys Invalidated |
|-------|----------------------|
| User updates profile | `user:{user_id}`, `user:{user_id}:section` |
| User adds friend | `friends:{user_id}`, `friends:{friend_id}`, `friends:{user_id}:ids` |
| User removes friend | `friends:{user_id}`, `friends:{friend_id}`, `friends:{user_id}:ids` |
| Group created | `user:{user_id}:groups` |
| Group deleted | `group:{group_id}`, `group:{group_id}:members`, `user_groups:*` |
| Member added | `group:{group_id}:members`, `avail:constellation:{group_id}` |
| Member removed | `group:{group_id}:members`, `avail:constellation:{group_id}` |
| Timetable imported | ALL `tt:*` keys, ALL `avail:*` keys (full cache flush) |
| Class transition | `avail:user:{user_id}:status`, `avail:constellation:{group_id}` for affected groups |

### Cache-Aside Pattern

```python
# CacheService wraps the Redis client

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_or_compute[T](
        self,
        key: str,
        ttl: int,
        compute: Callable[[], Awaitable[T]],
        serializer: Callable[[T], str] = json.dumps,
        deserializer: Callable[[str], T] = json.loads,
    ) -> T:
        """Classic cache-aside pattern with error handling.

        1. Try cache get(key)
        2. If hit → deserialize → return
        3. If miss → compute() → serialize → cache set(key, value, ttl) → return
        4. If cache is down → log warning → skip cache, call compute()
        """
        try:
            cached = await self.redis.get(key)
            if cached is not None:
                return deserializer(cached)
        except RedisError:
            logger.warning("Cache unavailable", key=key)

        value = await compute()

        try:
            await self.redis.setex(key, ttl, serializer(value))
        except RedisError:
            logger.warning("Cache write failed", key=key)

        return value
```

### Multi-Tier Caching (Future)

```
┌──────────────────────────────────────────────────────────────┐
│                    CACHE TIERS (Phase 2+)                     │
│                                                              │
│  Tier 1: In-Memory (dict cache, per-request)                 │
│  ├── Current request's data (avoid duplicate queries)        │
│  ├── TTL: request lifetime                                   │
│  └── Use: within a single /group/{id} request                │
│                                                              │
│  Tier 2: Redis (shared, cross-instance)                      │
│  ├── Cache-aside with TTL                                    │
│  ├── Handles: timetable, availability, friend list           │
│  └── Use: all requests, horizontal scale                     │
│                                                              │
│  Tier 3: PostgreSQL (source of truth)                        │
│  ├── Only queried on cache miss                              │
│  └── Use: cold start, cache eviction                         │
│                                                              │
│  Tier 4: Materialized View (future)                          │
│  ├── Pre-computed availability for every section × day      │
│  ├── Refreshed after timetable import                        │
│  └── Use: on-demand batch queries, analytics                │
└──────────────────────────────────────────────────────────────┘
```

### Rate Limiting Storage

```python
# Rate limiting uses Redis for atomic sliding window counters

# Sliding window algorithm:
# - Key: "ratelimit:user:{user_id}:{endpoint}"
# - Value: counter (INCR)
# - TTL: window duration (e.g., 60s)
# - Check: IF counter > limit → 429
# - Atomic: MULTI/EXEC or Lua script

RATE_LIMITS = {
    "auth/register":             {"limit": 5,   "window": 60},   # 5/min per IP
    "auth/refresh":              {"limit": 10,  "window": 60},   # 10/min per device
    "auth/logout":               {"limit": 30,  "window": 60},
    "users/search":              {"limit": 30,  "window": 60},   # 30/min per user
    "friends/add":               {"limit": 20,  "window": 60},   # 20/min per user
    "friends/remove":            {"limit": 20,  "window": 60},
    "groups/create":             {"limit": 10,  "window": 60},   # 10/min per user
    "availability/*":            {"limit": 100, "window": 60},   # 100/min per user (read)
    "admin/*":                   {"limit": 30,  "window": 60},   # 30/min per admin
    "default":                   {"limit": 100, "window": 60},   # fallback
}
```

---

## 15. Error Handling

### Domain Exception Hierarchy

```python
# app/core/exceptions.py

class ConstellationError(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

# --- Auth Module ---
class AuthenticationError(ConstellationError):
    def __init__(self, message="Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED", 401)

class TokenExpiredError(AuthenticationError):
    def __init__(self):
        super().__init__("Token has expired")

class TokenInvalidError(AuthenticationError):
    def __init__(self):
        super().__init__("Token is invalid")

class DeviceNotFoundError(AuthenticationError):
    def __init__(self):
        super().__init__("Device not recognized")

class DeviceLockedError(AuthenticationError):
    def __init__(self, retry_after: int):
        super().__init__(f"Device locked. Retry after {retry_after}s")
        self.retry_after = retry_after

class DeviceLimitExceededError(ConstellationError):
    def __init__(self):
        super().__init__("Maximum devices reached", "DEVICE_LIMIT", 403)

# --- User Module ---
class UserNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("User not found", "USER_NOT_FOUND", 404)

class UserAlreadyExistsError(ConstellationError):
    def __init__(self):
        super().__init__("User already registered", "USER_EXISTS", 409)

class SectionNotSelectedError(ConstellationError):
    def __init__(self):
        super().__init__("Section not selected", "SECTION_REQUIRED", 400)

# --- Friend Module ---
class FriendNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Friend not found", "FRIEND_NOT_FOUND", 404)

class FriendAlreadyExistsError(ConstellationError):
    def __init__(self):
        super().__init__("Already friends", "FRIEND_EXISTS", 409)

class CannotFriendSelfError(ConstellationError):
    def __init__(self):
        super().__init__("Cannot add yourself", "SELF_FRIEND", 400)

# --- Group Module ---
class GroupNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Group not found", "GROUP_NOT_FOUND", 404)

class NotGroupMemberError(ConstellationError):
    def __init__(self):
        super().__init__("Not a group member", "NOT_MEMBER", 403)

class NotGroupCreatorError(ConstellationError):
    def __init__(self):
        super().__init__("Only the creator can perform this action", "NOT_CREATOR", 403)

class GroupNameTooLongError(ConstellationError):
    def __init__(self):
        super().__init__("Group name exceeds 100 characters", "NAME_TOO_LONG", 400)

# --- Timetable Module ---
class ImportInProgressError(ConstellationError):
    def __init__(self):
        super().__init__("Import already in progress", "IMPORT_IN_PROGRESS", 409)

class ImportParseError(ConstellationError):
    def __init__(self, details: list[str]):
        super().__init__("Failed to parse workbook", "IMPORT_PARSE_ERROR", 422)
        self.details = details

class ImportValidationError(ConstellationError):
    def __init__(self, details: list[str]):
        super().__init__("Timetable validation failed", "IMPORT_VALIDATION_ERROR", 422)
        self.details = details

# --- Availability Module ---
class SectionNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Section not found", "SECTION_NOT_FOUND", 404)

class NoTimetableError(ConstellationError):
    def __init__(self):
        super().__init__("No timetable available", "NO_TIMETABLE", 404)
```

### Global Exception Handler

```python
# app/core/error_handlers.py

def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(ConstellationError)
    async def handle_domain_error(request, exc: ConstellationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
            headers={"X-Request-ID": request.state.request_id},
        )

    @app.exception_handler(ValidationError)  # Pydantic
    async def handle_validation_error(request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(IntegrityError)  # SQLAlchemy
    async def handle_integrity_error(request, exc: IntegrityError):
        await request.state.session.rollback()
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "CONFLICT",
                    "message": "Resource conflict",
                }
            },
        )

    @app.exception_handler(Exception)  # Catch-all
    async def handle_unexpected_error(request, exc: Exception):
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            request_id=request.state.request_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
```

### Error Response Contract

All errors follow the same shape:

```json
{
    "error": {
        "code": "FRIEND_NOT_FOUND",
        "message": "Friend not found"
    }
}
```

Validation errors include details:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": [
            {
                "loc": ["body", "roll_number"],
                "msg": "value is not a valid roll number pattern",
                "type": "value_error.str.regex"
            }
        ]
    }
}
```

---

## 16. Logging & Monitoring

### Structured Logging

```python
# app/core/logging.py

# Format: JSON lines (one log entry per line)
# Fields:
#   - timestamp: ISO 8601 (UTC)
#   - level: INFO, WARNING, ERROR, CRITICAL
#   - logger: module name
#   - request_id: UUID v7 (from middleware)
#   - user_id: UUID (if authenticated)
#   - method: HTTP method
#   - path: request path
#   - duration_ms: request duration
#   - status_code: response status
#   - message: human-readable (structured context as extra fields)

# No PII in logs:
# - Never log: roll_number, device_fingerprint, tokens, refresh tokens
# - Always mask: IP addresses (log prefix only: /24),
#   User IDs are UUIDs (not PII)

# Log levels:
#   DEBUG: SQL queries (dev only), detailed timing breakdown
#   INFO:  Request start/end, auth events, import start/end
#   WARNING: Slow queries (>500ms), rate limit exceeded, cache unavailable
#   ERROR:  Business errors (with request context), external service failures
#   CRITICAL: Database connection failure, startup failure (send to admin alert)

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(timestamp)s %(level)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}
```

### Health Checks

```python
# GET /health

# Response:
{
    "status": "healthy",                    # "healthy" | "degraded" | "unhealthy"
    "version": "1.0.0",
    "uptime_seconds": 123456,
    "checks": {
        "database": {
            "status": "healthy",
            "latency_ms": 2,
            "pool_used": 5,
            "pool_total": 20,
        },
        "cache": {
            "status": "healthy",
            "latency_ms": 1,
        },
        "storage": {
            "status": "healthy",
            "writable": true,
        },
    }
}

# Endpoint: GET /health (no auth)
# Endpoint: GET /health/ready (called by k8s readiness probe)
# Endpoint: GET /health/live (called by k8s liveness probe)
```

### Metrics

```python
# Prometheus metrics (via prometheus-fastapi-instrumentator or custom)

# RED Method metrics (for each endpoint):
#   Rate:     http_requests_total{method, path, status}
#   Errors:   http_request_errors_total{method, path, status}
#   Duration: http_request_duration_seconds{method, path, quantile}

# USE Method metrics (for resources):
#   Utilization:
#     - db_connection_pool_used
#     - db_connection_pool_idle
#     - cache_memory_used
#   Saturation:
#     - db_query_queue_depth (via pg_stat_activity)
#     - cache_hit_ratio (keyspace_hits / (keyspace_hits + keyspace_misses))
#   Errors:
#     - db_query_errors_total
#     - cache_errors_total

# Business metrics:
#   constellation_active_users          (users who made a request in last 24h)
#   constellation_friendships_total
#   constellation_groups_total
#   constellation_availability_queries_total
#   constellation_realtime_connections  (current WebSocket count)
```

### Tracing (Future)

```python
# OpenTelemetry for distributed tracing (when services split)

# Trace every request through the system:
# - Middleware creates a span for the request
# - Each database query is a child span
# - Each cache call is a child span
# - External service calls are child spans
# - Traces sampled: 100% for errors, 1% for success (adjustable)
```

---

## 17. Configuration

### Settings Schema

```python
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration.

    All values come from environment variables.
    No hardcoded configuration. No config files.

    Environment variables are prefixed with CONSTELLATION_:
    Example: CONSTELLATION_DATABASE__URL=postgresql+asyncpg://...
    """

    model_config = SettingsConfigDict(
        env_prefix="CONSTELLATION_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Application
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Database
    class DatabaseConfig(BaseModel):
        URL: PostgresDsn
        POOL_SIZE: int = 20
        MAX_OVERFLOW: int = 80
        ECHO: bool = False
    DATABASE: DatabaseConfig

    # Redis
    class RedisConfig(BaseModel):
        URL: RedisDsn
        POOL_SIZE: int = 10
    REDIS: RedisConfig

    # Auth
    class AuthConfig(BaseModel):
        JWT_SECRET: str
        JWT_ALGORITHM: str = "HS256"
        JWT_EXPIRY_MINUTES: int = 15
        REFRESH_EXPIRY_DAYS: int = 30
        DEVICE_FINGERPRINT_SALT: str
        ENUMERATION_PREVENTION_DELAY: float = 0.05  # 50ms
        MAX_DEVICES_PER_USER: int = 5
    AUTH: AuthConfig

    # CORS
    FRONTEND_URL: HttpUrl

    # Rate Limiting
    class RateLimitConfig(BaseModel):
        ENABLED: bool = True
        REDIS_PREFIX: str = "ratelimit"
    RATE_LIMIT: RateLimitConfig = RateLimitConfig()

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str | None = None

    # CORS
    CORS_ORIGINS: list[str] = []

    @model_validator(mode="after")
    def validate_environment(self):
        if self.ENVIRONMENT == "production" and self.DATABASE.ECHO:
            raise ValueError("Cannot enable SQL echo in production")
        return self


# Usage:
# from app.core.config import settings
# settings.DATABASE.URL  # validated PostgreSQL DSN
```

### Environment Variables

```bash
# .env.example — all required variables

CONSTELLATION_ENVIRONMENT=development
CONSTELLATION_DEBUG=true

CONSTELLATION_DATABASE__URL=postgresql+asyncpg://user:pass@localhost:5432/constellation
CONSTELLATION_DATABASE__POOL_SIZE=20
CONSTELLATION_DATABASE__MAX_OVERFLOW=80

CONSTELLATION_REDIS__URL=redis://localhost:6379/0
CONSTELLATION_REDIS__POOL_SIZE=10

CONSTELLATION_AUTH__JWT_SECRET=change-me-in-production
CONSTELLATION_AUTH__DEVICE_FINGERPRINT_SALT=change-me-too
CONSTELLATION_AUTH__JWT_EXPIRY_MINUTES=15
CONSTELLATION_AUTH__MAX_DEVICES_PER_USER=5

CONSTELLATION_FRONTEND_URL=http://localhost:3000

CONSTELLATION_LOG_LEVEL=INFO
```

---

## 18. Security Design

### Security Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                              │
│                                                                     │
│  Layer 1: Transport                                                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ TLS 1.3 everywhere                                          │    │
│  │ HSTS: max-age=31536000; includeSubDomains                   │    │
│  │ Certificate: Let's Encrypt (auto-renew via reverse proxy)   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Layer 2: Network                                                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Reverse proxy (Nginx) as sole entry point                   │    │
│  │ App runs on internal port (no direct exposure)              │    │
│  │ Rate limiting at proxy level (DDoS protection)              │    │
│  │ WAF rules: SQL injection patterns blocked at proxy          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Layer 3: Application                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ JWT auth with short expiry + refresh rotation               │    │
│  │ Device binding — every request tied to a registered device  │    │
│  │ Rate limiting per endpoint category                         │    │
│  │ Input validation at boundary (Pydantic)                     │    │
│  │ SQL injection: impossible (SQLAlchemy parameterized queries)│    │
│  │ CSRF: SameSite cookies + double-submit pattern              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Layer 4: Data                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Device fingerprints: SHA-256 + salt (at rest)               │    │
│  │ Refresh tokens: bcrypt (cost=10) at rest                    │    │
│  │ Roll numbers: NEVER in API responses                        │    │
│  │ PII minimization: store only essential data                 │    │
│  │ No plaintext secrets in logs                                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Layer 5: Database                                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ App role: only CRUD on app tables (no DDL)                  │    │
│  │ Connection pooling via PgBouncer (no direct DB)             │    │
│  │ Migrations run via Alembic (separate credentials)           │    │
│  │ Encrypted at rest (RDS encryption or LUKS)                  │    │
│  │ Automated backups (point-in-time recovery)                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Specific Threat Mitigations

| Threat | Mitigation | Implementation |
|--------|------------|----------------|
| Account enumeration | Constant-time response | Artificial delay on not-found paths |
| Brute force login | Rate limiting + device lock | 5 req/min + 15 min lock after 10 failures |
| Token theft (JWT) | Short expiry (15 min) + device binding | JWT has `did` claim, verified on every request |
| Token theft (refresh) | Rotation + device binding + bcrypt | New token invalidates old one, requires matching fingerprint |
| Session hijacking | Device binding | Refresh token + fingerprint must match stored pair |
| CSRF | SameSite cookies | All cookies set to `SameSite=Lax`, API rejects requests without origin header |
| XSS | CSP + input sanitization | `Content-Security-Policy: default-src 'none'` |
| SQL injection | Parameterized queries | SQLAlchemy ORM + raw SQL via text() with bound params |
| Data scraping | Rate limiting + minimal responses | 30 req/min for search, roll numbers never exposed |
| Replay attack | JWT `jti` + expiry | Unique token ID per JWT, short window |
| Man-in-the-middle | TLS 1.3 + HSTS | Enforced at proxy level, preload ready |
| Denial of service | Rate limiting + connection limits | App-level + proxy-level + cloud WAF |
| Privilege escalation | Authorization checks in services | Every service method checks: "does this user own this resource?" |

### Authorization Model

```python
# Authorization is enforced in the service layer, not the route layer.
# Every service method that accesses a resource first checks ownership/permission.

# Example: FriendService.remove_friend
async def remove_friend(self, user_id: UUID, friend_id: UUID) -> None:
    # Authorization: user_id must be the requester (from JWT)
    # user_id is NEVER taken from request body — always from auth context

    friendship = await self.friend_repo.find_bidirectional(user_id, friend_id)
    if not friendship:
        raise FriendNotFoundError()
    await self.friend_repo.delete(friendship.id)

# Example: GroupService.get_group_detail
async def get_group_detail(self, group_id: UUID, requesting_user_id: UUID) -> GroupDetail:
    # Authorization check: is requesting_user_id a member?
    is_member = await self.group_member_repo.exists(
        group_id=group_id, user_id=requesting_user_id
    )
    if not is_member:
        raise NotGroupMemberError()
    # ... fetch and return detail
```

---

## 19. Future Scaling Plan

### Phase 1: Modular Monolith (MVP)

```
 Architecture: Single FastAPI process + PostgreSQL + Redis
 Deployment: Docker Compose on single VPS
 Scale ceiling: 5,000 concurrent users, 15,000 total users
 Key constraint: WebSocket connections limited by single process
```

### Phase 2: Horizontal Scale

```
 Changes:
 - FastAPI behind load balancer (N → M instances)
 - Redis as shared cache + pub/sub
 - WebSocket with sticky sessions + Redis pub/sub for cross-instance messaging
 - PgBouncer for database connection pooling

 Deployment: Docker Swarm or Kubernetes
 Scale ceiling: 20,000 concurrent users, 100,000 total users
```

### Phase 3: Read Replicas + CQRS

```
 Changes:
 - PostgreSQL read replicas (1 primary, 2 replicas)
 - Read/write split in database layer:
   - Writes → primary
   - Reads → replicas (with 5s replication lag tolerance)
 - Availability queries go to read replicas
 - Materialized view for pre-computed availability:
   - View: user_id, day_of_week, start_time, end_time, is_free
   - Refreshed after timetable import
   - Reduces join complexity for common queries

 Deployment: Kubernetes with StatefulSets
 Scale ceiling: 50,000 concurrent users, 250,000 total users
```

### Phase 4: Service Split

```
 Changes:
 - Extract AvailabilityService into standalone service
 - Extract RealtimeService into standalone WebSocket service
 - API Gateway (Kong / Envoy) routes:
   /api/v1/auth/* → Auth Service
   /api/v1/users/* → User Service
   /api/v1/friends/* → Social Service
   /api/v1/groups/* → Social Service
   /api/v1/availability/* → Availability Service
   /ws/* → Realtime Service
 - Shared PostgreSQL but isolated connection pools
 - Event bus (Redis Streams / RabbitMQ) for cross-service communication:
   - Auth Service publishes: "user.registered", "user.logged_out"
   - Social Service publishes: "friend.added", "friend.removed"
   - Availability Service publishes: "status.changed"
   - Realtime Service consumes: all events → push to WebSocket clients

 Deployment: Kubernetes with Helm charts
 Scale ceiling: 200,000 concurrent users, 1M+ total users
```

### Phase 5: Full Microservices

```
 Changes:
 - Each service gets its own database schema (logical separation)
 - Shared Redis cache but separate namespaces per service
 - Dedicated Read replica per service
 - Service mesh (Istio/Linkerd) for mTLS, traffic management
 - gRPC for inter-service communication (internal), REST for external
 - Event sourcing for availability state (replayable, auditable)

 Deployment: Multi-cluster Kubernetes (regional)
 Scale ceiling: Multi-million users, multiple institutions
```

### Migration Triggers

| Trigger | Action | Phase |
|---------|--------|-------|
| Single process cannot handle WebSocket load | Deploy multiple WS instances with Redis pub/sub | Phase 2 |
| Database CPU > 70% during peak | Add read replicas, route reads | Phase 3 |
| Database connections exhausted | Add PgBouncer, tune pool sizes | Phase 2 |
| Deployment conflicts between teams | Split services along team boundaries | Phase 4 |
| Friend/group graph exceeds 100K edges | Consider graph database (Neo4j) for social features only | Phase 5 |
| Realtime latency > 2s consistently | Dedicated WebSocket service with per-connection goroutine | Phase 4 |
| Cache miss rate > 20% | Evaluate materialized views, pre-compute popular queries | Phase 3 |
| Single institution exceeded | Multi-tenant isolation, shared-nothing architecture | Phase 5 |

---

## Appendix: Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | UUID v7 for primary keys | Time-ordered → B-tree friendly index performance, no sequential ID guessing |
| 2 | `expire_on_commit=False` | Prevents lazy-load errors after session commit, forces explicit refresh |
| 3 | Services receive primitives, not request objects | Testability (no HTTP mocking), separation of concerns |
| 4 | Repositories return ORM models | Keeps repository layer simple; mapping to schemas happens in services |
| 5 | Cache-aside with fallback | Cache failure is not a system failure; degrade gracefully |
| 6 | Background thread pool for Excel parsing | openpyxl is synchronous and CPU-bound; would block the event loop |
| 7 | All-or-nothing timetable import | Partial import would leave inconsistent data; single transaction |
| 8 | Roll numbers never in API responses | Privacy: roll numbers are PII, UUIDs are opaque |
| 9 | No server-side sessions | Stateless JWT enables horizontal scaling without shared session store |
| 10 | Domain exceptions with HTTP codes | Maps cleanly to FastAPI error handlers; typed exceptions for testing |
| 11 | One active device per session | Security: old device tokens are revoked, account can't be used from multiple places |
| 12 | Service layer handles authorization | Route layer should not decide who can do what; business rules in one place |
| 13 | Batch queries return dicts, not lists | Enables O(1) lookup in service layer, avoids N+1 in logic |
| 14 | Pydantic internal schemas for DTOs | ORM models never leak to API; internal schemas are stable surface |
| 15 | Rate limiting in middleware + Redis | Centralized, consistent across all endpoints, survives restarts |
