# Constellation — Future Roadmap

## Phase 1: MVP (Weeks 1-8)

### Week 1-2: Foundation
- [ ] Set up monorepo structure (frontend/ + backend/)
- [ ] Docker Compose: PostgreSQL + FastAPI + Next.js
- [ ] Database models and initial Alembic migration
- [ ] Device-based auth (register, refresh, logout)
- [ ] Frontend login page + auth store + API client

### Week 3-4: Timetable Import
- [ ] Excel parser (openpyxl): sheet → section → course → timeslot
- [ ] Data normalizer (dedup, validate, link)
- [ ] Bulk insert with transaction
- [ ] Admin import page (upload, progress, status)
- [ ] End-to-end test: upload workbook → verify DB

### Week 5-6: Core Availability
- [ ] Availability service: is_free, current_class, next_event
- [ ] `/availability/me` endpoint
- [ ] `/availability/me/schedule` endpoint
- [ ] Dashboard page: current status, schedule timeline
- [ ] Onboarding flow: section selection

### Week 7-8: Social Graph
- [ ] Friend endpoints (add, remove, search, list)
- [ ] Group endpoints (CRUD, members)
- [ ] Friend comparison endpoint
- [ ] Group availability endpoint
- [ ] Friends page + Group pages
- [ ] Basic constellation visualization (Canvas)

---

## Phase 2: Social Enhancement (Weeks 9-12)

- [ ] WebSocket infrastructure
- [ ] Real-time friend status updates
- [ ] Real-time constellation updates
- [ ] Friend requests (accept/decline flow)
- [ ] Group invites (suggested members based on common friends)
- [ ] User avatars (initials, then upload)
- [ ] Push notifications (browser): class starting, friend free
- [ ] Home screen widget (PWA)
- [ ] Constellation animation improvements (pulsing stars, connection glow)

---

## Phase 3: Intelligence (Weeks 13-16)

- [ ] "Best time to meet" suggestion algorithm
- [ ] Study group formation (match: same courses + common free slots)
- [ ] Attendance tracking (student self-declared)
- [ ] Class reminders (15 min before)
- [ ] Calendar export (ICS format)
- [ ] Weekly timetable wallpaper generator
- [ ] Constellation sharing (export as image)

---

## Phase 4: Campus Scale (Weeks 17-24)

- [ ] Multi-semester support (archive old, activate new)
- [ ] Academic calendar (holidays, exam periods, reading days)
- [ ] Campus events integration (import events, show schedule conflicts)
- [ ] Room booking (based on room availability in timetable)
- [ ] Admin dashboard (user analytics, import history, error logs)
- [ ] Multi-institution support (tenant isolation)
- [ ] Performance optimization: Redis caching, query tuning

---

## Phase 5: Platform (6+ months)

- [ ] Native mobile apps (React Native)
- [ ] Student marketplace (buy/sell books, notes, equipment)
- [ ] Study streak gamification
- [ ] Course reviews + ratings
- [ ] Alumni network features
- [ ] Public API for third-party integrations
- [ ] Integration with LMS (Moodle, Canvas, Blackboard)
- [ ] Real-time study rooms (video/voice) based on availability

---

## Architectural Evolution Path

```
Phase 1: Monolith
  single FastAPI process + single PostgreSQL

Phase 2: Monolith + Cache
  FastAPI + Redis (cache/pubsub) + PostgreSQL
  WebSocket on same FastAPI process

Phase 3: Monolith + Workers
  FastAPI + Celery (background tasks) + Redis + PostgreSQL
  WebSocket on dedicated FastAPI instances (sticky sessions)

Phase 4: Split Social Graph
  Social Service (FastAPI) + Availability Service (FastAPI)
  API Gateway routing
  Shared PostgreSQL (read replicas per service)

Phase 5: Microservices (if needed)
  Auth Service | User Service | Social Service | Availability Service
  Notification Service | Timetable Service
  Event bus (Kafka/RabbitMQ) for inter-service communication
  Service-per-team ownership
```

**Key principle**: Do not decompose until there is a demonstrated need (team size > 5, deployment conflicts, scaling bottlenecks). The modular monolith design already has well-defined service boundaries. Splitting is a packaging change, not a rewrite.
