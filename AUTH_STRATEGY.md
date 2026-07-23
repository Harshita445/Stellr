# Constellation — Authentication Strategy

## Passwordless Device-Based Auth Flow

### Registration (first use)

```
Device                           Server
  │                                │
  │── POST /auth/register ────────→│
  │   { roll_number,               │
  │     device_fingerprint,        │
  │     device_name }              │
  │                                ├── Look up user by roll_number
  │                                ├── Create user if not exists
  │                                ├── Store device fingerprint (hashed)
  │                                ├── Generate JWT (15m expiry)
  │                                ├── Generate refresh token (random UUID)
  │                                └── Store refresh token hash
  │←── { access_token,             │
  │      refresh_token, user }     │
  │                                │
  │  Store tokens in               │
  │  Zustand (persisted)           │
```

### Subsequent requests

```
  │── Authorization: Bearer <jwt> ─→│
  │                                ├── Verify JWT signature + expiry
  │                                ├── Extract user_id from sub claim
  │                                └── Proceed
```

### Token refresh (when JWT expired)

```
  │── POST /auth/refresh ──────────→│
  │   { refresh_token,              │
  │     device_fingerprint }        │
  │                                ├── Verify refresh token hash
  │                                ├── Verify device fingerprint matches
  │                                ├── Rotate refresh token (new one issued)
  │                                ├── Issue new JWT
  │←── { access_token,             │
  │      refresh_token }           │
```

---

## Token Design

```json
// JWT Payload
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user UUID
  "did": "660e8400-e29b-41d4-a716-446655440001",   // device UUID
  "rol": "2021CSB1078",                              // roll number
  "iat": 1700000000,                                 // issued at
  "exp": 1700000900                                  // expires (15 min)
}

// Refresh Token
// Random 128-bit UUID, stored as bcrypt hash in devices table
// Rotated on each use (old hash replaced by new hash)
// 30-day expiry (enforced by checking last_used_at)
```

---

## Security Properties

| Property | Implementation |
|----------|---------------|
| **No passwords** | Device fingerprint + refresh token replaces password |
| **Device binding** | Refresh token is only valid when paired with matching device_fingerprint |
| **Token rotation** | Refresh token changes on every use; stolen token is single-use |
| **Limited blast radius** | 15-minute JWT; compromised token is short-lived |
| **Revocation** | Delete device row → invalidates all tokens for that device |
| **Collision resistance** | UUID v4 for tokens; 128 bits of entropy |

---

## Roll Number Trust Model

Since this is a campus app, we have two verification modes:

**Mode 1 (trusted network)**: If the request originates from the campus network or institutional SSO proxy, trust the roll number implicitly. Skip OTP.

**Mode 2 (external)**: Send OTP to `roll_number@institution.edu` email. User must enter OTP within 5 minutes.

**Why this is acceptable**: The app is internal to a college. Misuse requires knowing someone's roll number AND having access to their device. The risk profile is low. OTP can be added later for higher-value deployments.

---

## Frontend Auth Integration

```typescript
// api-client.ts (axios interceptors)
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const { refreshToken } = useAuthStore.getState();
      if (refreshToken) {
        const newTokens = await refreshTokens(refreshToken);
        useAuthStore.getState().setTokens(newTokens.access, newTokens.refresh);
        error.config.headers.Authorization = `Bearer ${newTokens.access}`;
        return api(error.config); // retry
      }
      // No refresh token → force logout
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```
