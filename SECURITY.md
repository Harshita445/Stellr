# Constellation — Security Considerations

## Threat Model

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| Stolen JWT | Account access for 15 min | Medium | Short expiry, HTTPS-only |
| Stolen refresh token | Account access for 30 days | Low | Device binding, rotation, bcrypt hashing |
| Device theft | Account access | Low | Remote revocation (admin panel) |
| Roll number guessing | Account creation as another user | Medium | OTP verification (v2) |
| CSRF | Unauthorized actions | Medium | SameSite cookies, double-submit cookie pattern |
| XSS | Token theft, data exfiltration | Medium | CSP headers, input sanitization, HttpOnly cookies for refresh token |
| SQL injection | Data exfiltration | Low | SQLAlchemy parameterized queries |
| Brute force auth | Account takeover | Low | Rate limiting (5 req/min per IP) |
| Timetable manipulation | Incorrect availability | Very Low | Admin-only import, section assignment is immutable after onboarding |
| Friend graph enumeration | Stalker risk | Medium | Search returns minimal info, only existing friends see schedule details |

---

## Security Controls

### Transport Security
- TLS 1.3 enforced at reverse proxy level
- HSTS header (max-age=31536000; includeSubDomains)
- All cookies set with `Secure; HttpOnly; SameSite=Lax`

### API Security
- Rate limiting per endpoint category
- Request size limits (body: 1MB, file upload: 10MB)
- CORS restricted to frontend origin only
- Authorization header required for all protected endpoints

### Data Protection
- Device fingerprints hashed with SHA-256 + per-app salt
- Refresh tokens hashed with bcrypt (cost factor 10)
- Roll numbers treated as PII; not exposed in friend search results
- No plaintext secrets in logs (Pydantic's `SecretStr` for sensitive fields)

### File Upload Security
- Validate MIME type (must be `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
- Scan for macros (reject if any VBA)
- Parse in sandboxed environment (separate process)
- Maximum file size: 10MB
- Maximum rows per sheet: 10,000
- Maximum sheets: 20

### Database Security
- Application connects with minimal-privilege role (SELECT/INSERT/UPDATE/DELETE on app tables only)
- No DDL permissions for app role (migrations run separately)
- Connection pooling via PgBouncer (not direct connections)
- Prepared statements for all queries

---

## Privacy by Design

- **Friend list is private**: Not visible to other users
- **Group membership is visible only to members**: Group detail endpoint checks membership
- **Schedule is private by default**: Only visible to friends you've added
- **Search is gated**: User search requires at least 3 characters of a roll number
- **No global feed**: No "all users" or "discover" functionality
- **Data retention**: User deletion cascades to all associated data (friendships, memberships)
