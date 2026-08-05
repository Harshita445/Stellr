# Constellation — Database Schema

## Entity-Relationship Diagram

```
users ────< devices
  │
  ├──── section_id ──── sections ────< timetable_entries >──── courses
  │                                                    │
  │                                                    └──── timeslots
  │
  ├────< friends >──── users (friend)
  │
  └────< group_members >──── groups
```

---

## Table Definitions

### `users`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK, default gen_random_uuid() | |
| roll_number | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | e.g., "2021CSB1078" |
| display_name | VARCHAR(100) | | Auto-generated from roll if not set |
| section_id | UUID | FK → sections.id, NOT NULL | Set during onboarding |
| avatar_url | TEXT | | Nullable; initials fallback on frontend |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Index: `idx_users_roll_number` on `roll_number`
- Index: `idx_users_section` on `section_id`

### `devices`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | |
| device_fingerprint | VARCHAR(255) | NOT NULL, INDEX | SHA-256 of device identifier |
| device_name | VARCHAR(100) | | e.g., "iPhone 15", "MacBook Pro" |
| refresh_token_hash | VARCHAR(255) | NOT NULL | bcrypt hash of refresh token |
| last_used_at | TIMESTAMPTZ | NOT NULL, default now() | |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Index: `idx_devices_fingerprint` on `device_fingerprint`

**Why hash the fingerprint**: Even though the fingerprint is already a hash of device characteristics, we hash it again at rest. Defense in depth. The hash is deterministic (same fingerprint → same hash) so we can look up by it.

### `sections`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(100) | NOT NULL | e.g., "CSE-A", "ECE-B" |
| department | VARCHAR(100) | NOT NULL | e.g., "Computer Science" |
| semester | INTEGER | NOT NULL | 1-8 |
| academic_year | VARCHAR(20) | NOT NULL | e.g., "2025-2026" |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Unique: `uq_section` on `(name, department, semester, academic_year)`

### `courses`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| code | VARCHAR(20) | NOT NULL | e.g., "CS201" |
| name | VARCHAR(200) | NOT NULL | e.g., "Data Structures" |
| department | VARCHAR(100) | | Nullable; inferred from context |

- Unique: `uq_course` on `(code, department)`

### `timeslots`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| day_of_week | SMALLINT | NOT NULL, CHECK (0-6) | ISO: 0=Monday |
| start_time | TIME | NOT NULL | |
| end_time | TIME | NOT NULL | |
| slot_type | VARCHAR(20) | NOT NULL | "lecture", "lab", "tutorial" |
| venue | VARCHAR(100) | | Room/building |

- Index: `idx_timeslots_day_time` on `(day_of_week, start_time, end_time)`

This is the most critical index. It powers every availability query.

### `timetable_entries`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| section_id | UUID | FK → sections.id, NOT NULL | |
| course_id | UUID | FK → courses.id, NOT NULL | |
| timeslot_id | UUID | FK → timeslots.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Unique: `uq_tt_entry` on `(section_id, timeslot_id)` — prevents duplicate entries
- Index: `idx_tt_section_course` on `(section_id, course_id)` — for "what courses does section X have?"

### `friends`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| friend_id | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Unique: `uq_friendship` on `(LEAST(user_id, friend_id), GREATEST(user_id, friend_id))`
- Check: `user_id <> friend_id`

**Bidirectional design**: A single row represents a friendship. `LEAST/GREATEST` ensures only one row regardless of who initiated.

- Index: `idx_friends_user` on `user_id`
- Index: `idx_friends_friend` on `friend_id`

### `groups`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(100) | NOT NULL | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |

### `group_members`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| group_id | UUID | FK → groups.id, NOT NULL, ON DELETE CASCADE | |
| user_id | UUID | FK → users.id, NOT NULL | |
| joined_at | TIMESTAMPTZ | NOT NULL, default now() | |

- Unique: `uq_group_member` on `(group_id, user_id)`
- Index: `idx_gm_user` on `user_id`

---

## Normalization Rationale

The timetable is broken into 5 tables (sections, courses, timeslots, timetable_entries) rather than stored as JSONB or a flat table. This is deliberate:

1. **Query efficiency**: The `timetable_entries` join with `timeslots` on indexed columns produces sub-millisecond lookups.
2. **Data integrity**: Foreign keys prevent orphaned entries, invalid times, duplicate assignments.
3. **Normalized storage**: Time ranges are not duplicated across students sharing a section. A section with 60 students = 1 entry, not 60.
4. **Flexibility**: A course can appear in multiple sections without data duplication.

**Why not JSONB**: JSONB would require parsing on every request, cannot be indexed for range queries efficiently, and lacks referential integrity. For a schedule app where correctness of time ranges matters, normalized relational storage is the right choice.
