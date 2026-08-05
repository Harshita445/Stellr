# Constellation — Scalability Considerations

## Scale Expectations

| Metric | MVP Estimate | Growth Ceiling |
|--------|-------------|----------------|
| Users | 1,000 | 15,000 (single institution) |
| Concurrent users | 200 | 3,000 |
| Timetable entries | 20,000 | 300,000 |
| Friendships | 5,000 | 200,000 |
| Groups | 500 | 15,000 |
| Availability queries/sec | 10 | 500 |
| Timetable imports | 1/semester | 1/semester |

**Conclusion**: At this scale, PostgreSQL with proper indexing handles everything without vertical scaling concerns. The system is I/O bound, not CPU bound.

---

## Bottleneck Analysis

### Potential Bottleneck 1: Availability Queries
- Pattern: `SELECT ... FROM timetable_entries JOIN timeslots WHERE section_id = X AND day_of_week = Y`
- Index usage: `idx_tt_section` → index scan on section_id
- Performance: ~2ms per query at 300K rows
- At 500 QPS: ~1 second total DB time per second → ~1.0 DB load factor → OK but tight
- **Mitigation**: Add Redis cache keyed by `availability:{section_id}:{day}:{hour_bucket}`, TTL 5 min

### Potential Bottleneck 2: Group Overlap Calculation
- Pattern: For N members, fetch timetable_entries for N sections, compute intersection
- At N=10: ~10 queries × 2ms = 20ms DB time + 2ms compute = ~22ms
- At 50 QPS on groups: ~1.1s DB time → unsustainable
- **Mitigation**: Cache group overlap results with 1-minute TTL. Group availability only changes at fixed times (class end/start).

### Potential Bottleneck 3: Friend Status Dashboard
- Pattern: Fetch friends list (1 query) → for each friend, check availability (N queries)
- At 50 friends: 1 + 50 = 51 queries per dashboard load
- At 100 concurrent dashboard loads: 5,100 queries
- **Mitigation**: Batch availability check. Single query: `SELECT user_id, is_free FROM availability_cache WHERE user_id IN (:friend_ids)`. Or use a dedicated materialized view refreshed every minute.

### Potential Bottleneck 4: Timetable Import
- Excel workbook with 20 sheets, 50 sections, 200 courses, 1000 timeslot entries
- Parse time: ~5 seconds
- DB insert time: ~2 seconds (batch insert)
- **Mitigation**: Run as FastAPI BackgroundTask or Celery task. User gets 202 Accepted immediately.

---

## Caching Strategy

```
┌────────────────────────────────────────────────────────────┐
│                    CACHE LAYER (Redis, Phase 2+)            │
│                                                            │
│  availability:{section_id}:{day}:{hour} → bool            │
│    TTL: 5 min (timetable is static; cache for duration)    │
│    Computation: Is this section in class during this hour? │
│                                                            │
│  group_overlap:{group_id}:{date} → CommonSlot[]           │
│    TTL: 1 min                                              │
│    Computation: Intersection of all members' free slots    │
│                                                            │
│  user_friends:{user_id} → Friend[]                         │
│    TTL: 30s (friend list can change)                      │
│                                                            │
│  import_lock (distributed lock for upload)                 │
│    TTL: 5 min                                              │
│    Prevents concurrent imports                             │
└────────────────────────────────────────────────────────────┘
```

---

## Database Scaling

### Phase 1 (MVP)
- Single PostgreSQL instance (db.r6g.large: 2 vCPU, 16GB RAM)
- Connection pool: 50 connections
- WAL archiving for point-in-time recovery

### Phase 2 (Growth)
- PgBouncer for connection pooling
- Read replica for availability queries
- Application routes writes to primary, reads to replica

### Phase 3 (Scale)
- TimescaleDB extension for time-series optimization
- Table partitioning by academic_year for timetable_entries
- Connection pooling across multiple read replicas

---

## Application Scaling

FastAPI is stateless (JWT auth, no server-side sessions). Horizontal scaling is trivial:

```
Client → Load Balancer → FastAPI Instance 1
                      → FastAPI Instance 2
                      → FastAPI Instance N
```

No sticky sessions needed. WebSocket (Phase 3) requires sticky sessions or a pub/sub layer:

```
WebSocket Client → Load Balancer (sticky) → FastAPI WS Instance
                                            ↓
                                         Redis Pub/Sub
                                            ↓
                                         All WS Instances
```
