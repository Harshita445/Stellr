# Constellation — API Design

## Base URL

All endpoints are prefixed with `/api/v1/`.

---

## Authentication Endpoints

```
POST   /api/v1/auth/register
    Register a new device + user
    Body: { roll_number, device_fingerprint, device_name? }
    Response: { access_token, refresh_token, user }
    Status: 201 Created
    Rate: 5/min per IP

POST   /api/v1/auth/verify-otp
    Verify roll number ownership (v2, optional)
    Body: { roll_number, otp }
    Response: { verified: true }

POST   /api/v1/auth/refresh
    Rotate tokens
    Body: { refresh_token, device_fingerprint }
    Response: { access_token, refresh_token }
    Rate: 10/min per device

POST   /api/v1/auth/logout
    Invalidate device session
    Header: Authorization: Bearer <access_token>
    Response: 204 No Content
```

---

## User Endpoints

```
GET    /api/v1/users/me
    Own profile with section info
    Response: { id, roll_number, display_name, section, avatar_url, created_at }

PATCH  /api/v1/users/me
    Update profile (select section, set display name)
    Body: { display_name?, section_id? }
    Response: updated user

GET    /api/v1/users/search
    Search users by roll number or display name
    Query: ?q=2021CSB&limit=10
    Response: [{ id, roll_number, display_name }]
    Note: Only returns basic info, not full profile
```

---

## Friend Endpoints

```
GET    /api/v1/friends
    List friends with availability status
    Query: ?status=free (optional filter)
    Response: [{ user: { id, display_name }, is_free: bool, since: datetime? }]

POST   /api/v1/friends
    Add friend by user ID
    Body: { friend_id }
    Response: { id, user, friend, created_at }
    Status: 201 Created
    Errors: 404 (user not found), 409 (already friends)

DELETE /api/v1/friends/:friend_id
    Remove friend
    Response: 204 No Content
```

---

## Availability Endpoints

```
GET    /api/v1/availability/me
    Current availability status
    Query: ?at=2026-07-23T14:30:00Z (optional, defaults to server now)
    Response: {
        status: "free" | "in_class",
        current_class: { course, venue, ends_at } | null,
        next_event: { type, course?, starts_at, ends_at }
    }

GET    /api/v1/availability/me/schedule
    Full schedule for a day or week
    Query: ?date=2026-07-23&view=day|week
    Response: {
        date: "2026-07-23",
        slots: [{ start, end, course, venue, type }],
        free_slots: [{ start, end }]
    }

GET    /api/v1/availability/compare/:friend_id
    Compare availability with a friend
    Query: ?date=2026-07-23
    Response: {
        user: { id, display_name },
        friend: { id, display_name },
        date: "2026-07-23",
        both_free_now: bool,
        common_free_slots: [{ start, end }],
        next_common_slot: { start, end } | null
    }
    Errors: 403 (not friends with this user)

GET    /api/v1/availability/compare/batch
    Compare with multiple friends at once
    Body: { friend_ids: [uuid, ...] }
    Response: {
        results: [{ friend_id, both_free_now, next_common_slot }]
    }
```

---

## Group Endpoints

```
GET    /api/v1/groups
    List groups the user belongs to
    Response: [{
        id, name, member_count,
        free_now_count,       # how many are currently free
        next_overlap: { start, end } | null
    }]

POST   /api/v1/groups
    Create a new group
    Body: { name, member_ids: [uuid, ...] }
    Response: { id, name, members, created_at }
    Status: 201 Created

GET    /api/v1/groups/:group_id
    Group detail with constellation state
    Response: {
        id, name, created_by,
        members: [{ user: { id, display_name }, is_free: bool }],
        constellation: {   # computed for frontend
            all_free: bool,
            connections: [[user_id, user_id], ...],
            free_count: int
        },
        next_overlap: { start, end } | null,
        common_free_slots: [{ start, end }]
    }
    Errors: 403 (not a member)

PATCH  /api/v1/groups/:group_id
    Rename group
    Body: { name }
    Response: updated group
    Errors: 403 (not creator)

DELETE /api/v1/groups/:group_id
    Delete group (creator only)
    Response: 204 No Content
    Errors: 403 (not creator)

POST   /api/v1/groups/:group_id/members
    Add members to group
    Body: { member_ids: [uuid, ...] }
    Response: { members: [...] } (updated list)
    Errors: 403 (not a member)

DELETE /api/v1/groups/:group_id/members/:user_id
    Remove member from group
    Response: 204 No Content
    Errors: 403 (not creator or self-removal allowed)
```

---

## Admin Endpoints

```
POST   /api/v1/admin/timetable/import
    Upload timetable workbook
    Multipart: file (Excel .xlsx)
    Response: {
        task_id,
        status: "processing",
        sheets_detected: int,
        sections_detected: int
    }
    Status: 202 Accepted
    Note: Runs as background task

GET    /api/v1/admin/timetable/import/:task_id/status
    Check import status
    Response: {
        status: "processing" | "completed" | "failed",
        sections_imported: int,
        courses_imported: int,
        entries_imported: int,
        errors: [string]
    }
```

---

## Error Response Format

```json
{
    "detail": {
        "code": "FRIEND_NOT_FOUND",
        "message": "User with the specified ID is not your friend"
    }
}
```

### Standard HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (background task) |
| 204 | Deleted/Updated (no body) |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (not a friend, not a member) |
| 404 | Not found |
| 409 | Conflict (already exists) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |
| 500 | Internal error |
