# Constellation — Auth Token Flow

## Overview

Authentication is passwordless and device-bound. There are no passwords, emails, or OTPs. A user is identified by their roll number on exactly one endpoint (`POST /api/v1/auth/register`). After that, all communication uses internal UUIDs.

## Endpoints

### `POST /api/v1/auth/register` (no auth required)

**Request:**
```json
{
  "display_name": "Alice",
  "roll_number": "2021CSB1078",
  "section_code": "CSE3A"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "Alice",
    "section_code": "CSE3A"
  },
  "tokens": {
    "access_token": "<jwt>",
    "refresh_token": "<uuid>",
    "device_id": "660e8400-e29b-41d4-a716-446655440001",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Roll number is NEVER returned in the response body.** This is a hard rule — no endpoint ever exposes the roll number.

**Device binding:** The server generates a new `device_id` on every registration call for the same roll number, and deletes all previous device records for that user (transactionally). This enforces **one active device per user** — registering from a new device kicks out the old one.

**Rate limiting:** 5 requests per IP per 60 seconds (in-memory, no Redis).

### `POST /api/v1/auth/refresh` (no auth required)

**Request:**
```json
{
  "refresh_token": "<uuid>"
}
```
**Header:** `X-Device-ID: <device-uuid>`

**Response (200):**
```json
{
  "access_token": "<new-jwt>",
  "refresh_token": "<new-uuid>",
  "token_type": "bearer",
  "expires_in": 900
}
```

Refresh tokens are **rotated on every use** — the old refresh token becomes invalid immediately.

## Token Format

### JWT (access token)
- Algorithm: HS256
- Expiry: 15 minutes (tradeoff: short enough to limit blast radius of theft, long enough to avoid excessive refresh calls)
- Payload:
  ```json
  {
    "sub": "user-uuid",
    "did": "device-uuid",
    "iat": 1700000000,
    "exp": 1700000900,
    "jti": "unique-token-id"
  }
  ```
- The JWT does NOT contain the roll number — even though JWTs are signed, the payload is readable (base64). Roll numbers never leave the server except during the one-time register call.

### Refresh Token
- Random UUID v4 (128 bits of entropy)
- Stored as bcrypt hash (cost=10) in the `devices` table
- Valid for 30 days since `last_used_at` (enforced as soft expiry — unused tokens older than 30 days should be cleaned up)

## How Phase 6 (friends/groups) should use auth

Every authenticated endpoint requires two headers:

```
Authorization: Bearer <jwt>
X-Device-ID: <device-uuid>
```

Use the `get_current_user` dependency from `app/api/deps.py`:

```python
from app.api.deps import get_current_user

@router.get("/friends")
async def list_friends(
    current_user: dict = Depends(get_current_user),
    ...
):
    user_id = current_user["user_id"]
    # user_id is a UUID — use it for all friend/group lookups
```

The dependency:
1. Extracts and validates the JWT from the `Authorization` header
2. Verifies the `device_id` in the JWT `did` claim matches the `X-Device-ID` header
3. Raises `401 AuthenticationError` if either check fails
4. Returns `{"user_id": UUID, "device_id": UUID}`

**Never accept a roll number in any endpoint other than `/auth/register`.** Friend search, group member lookup, etc. use UUIDs only. This is the primary anti-scraping measure.

## Anti-Enumeration Measures

1. Same response shape for new and existing roll numbers on `/auth/register`
2. Artificial 50ms delay on the "create user" path to match the "find user" query time
3. Roll number never appears in API responses, URL paths, or query parameters
4. Rate limiting (5/min/IP) on the register endpoint
5. In-memory rate limiter — no Redis dependency for MVP
