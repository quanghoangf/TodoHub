# TodoHub - Digital Habit Tracker Implementation Plan

This is a **phase-by-phase implementation plan** for transforming the existing FastAPI template into the Digital Habit Tracker & Streak System.
Each phase builds upon the existing domain-driven architecture and follows the established patterns in the codebase.

The project leverages the existing:
- Domain-driven design with separate domains (auth, users, items)
- Repository pattern for data access
- Service layer for business logic
- Dependency injection with service containers
- Alembic migrations and PostgreSQL
- React frontend with TypeScript

---

# Phase 0 — Adapt existing template for habit tracking ✅ COMPLETED

**Objective:** Transform the existing "items" domain into "habits" and update the architecture to support habit-specific features.

**Priority:** High
**Complexity:** Low → Medium

**Status:** ✅ Foundation is ready - we have:
* ✅ Repo with domain-driven structure
* ✅ Docker Compose dev stack (Postgres, Redis optional)
* ✅ FastAPI app with OpenAPI and domain separation
* ✅ Alembic migrations system
* ✅ React frontend with auto-generated TypeScript client
* ✅ Authentication and user management

**Next:** Ready to proceed to Phase 1

---

# Phase 1 — Transform Items to Habits with Timezone Support

**Objective:** Transform the existing "items" domain into "habits" with timezone support and habit-specific features.

**Priority:** Highest
**Complexity:** Medium

**Current Status:** 
* ✅ JWT auth already implemented in `app/domains/auth/`
* ✅ User model exists in `app/domains/users/models.py`
* ✅ Items CRUD exists in `app/domains/items/` (to be transformed)

**Deliverables**

* Add timezone field to User model
* Transform Item model into Habit model with schedule support
* Update existing CRUD operations for habits
* Frontend habit management interface

**DB model updates**

```sql
-- Add to existing users table
ALTER TABLE user ADD COLUMN timezone text default 'UTC';

-- Transform items table to habits
-- (or create new habits table and migrate data)
habits (
  id uuid primary key,
  owner_id uuid references user(id) on delete cascade,
  title text not null,              -- reuse from items
  description text,                 -- reuse from items  
  category text,
  schedule jsonb,                   -- NEW: { "type":"daily" } or {"type":"weekly","days":[1,3,5]}
  start_date date,                  -- NEW
  backfill_window_hours int default 48,  -- NEW
  created_at timestamptz,           -- existing
  updated_at timestamptz            -- existing
);
```

**Updated API endpoints (building on existing)**

* ✅ `POST /api/v1/auth/login` (already exists)
* ✅ `GET /api/v1/users/me` (already exists)
* **UPDATE** `GET /api/v1/habits/` (transform from items)
* **UPDATE** `POST /api/v1/habits/` (transform from items)  
* **UPDATE** `GET /api/v1/habits/{id}` (transform from items)
* **NEW** `PUT /api/v1/users/me/timezone` (set user timezone)

**Tasks**

1. Add timezone field to User model and create migration
2. Transform `app/domains/items/` → `app/domains/habits/`:
   - Update models.py with habit-specific fields
   - Update schemas.py with schedule validation
   - Update service.py with habit business logic
   - Update router.py endpoints
3. Update repository pattern for habits
4. Update frontend client and components
5. Add timezone selector to user settings

**Acceptance criteria**

* User can set/update their timezone
* Habit CRUD operations work with schedule validation
* Frontend displays habits instead of items
* All existing tests pass with habit domain

---

# Phase 2 — Habit Logging & Streak System

**Objective:** Add habit logging capability with timezone-aware streak calculation to the existing architecture.

**Priority:** Highest  
**Complexity:** High (timezone/streak logic is complex)

**Deliverables**

* New `habit_logs` domain following the existing domain pattern
* Timezone-aware logging with idempotency
* Streak calculation service with caching
* Frontend logging interface with real-time streak updates

**New Domain Structure**

Following the existing pattern in `app/domains/`:

```
app/domains/habit_logs/
├── __init__.py
├── models.py          # HabitLog, StreakCache models  
├── schemas.py         # LogCreate, LogResponse, StreakResponse
├── repository.py      # HabitLogRepository, StreakRepository
├── service.py         # HabitLogService (with streak calculation)
└── router.py          # Logging endpoints
```

**DB models (new tables)**

```sql
habit_logs (
  id uuid primary key,
  habit_id uuid references habits(id) on delete cascade,
  user_id uuid references user(id) on delete cascade, 
  local_date date not null,         -- date in user's timezone
  recorded_at timestamptz default now(),
  idempotency_key text,
  meta jsonb,
  unique (habit_id, local_date)     -- prevents duplicate logical logs
);

streaks_cache (
  habit_id uuid primary key references habits(id),
  current_streak int default 0,
  longest_streak int default 0,
  last_updated timestamptz default now()
);
```

**New API endpoints**

* `POST /api/v1/habits/{id}/logs` - Log habit completion (idempotent)
* `GET /api/v1/habits/{id}/logs` - Get habit log history  
* `GET /api/v1/habits/{id}/streak` - Get current/longest streak
* `DELETE /api/v1/habits/{id}/logs/{date}` - Remove log (recalc streak)

**Integration with existing architecture**

* Update `app/domains/habits/service.py` to include streak data in responses
* Update `app/core/container.py` to include HabitLogService
* Create migration in `app/database/migrations/`
* Update frontend components to show logging interface

**Tasks**

1. Create habit_logs domain following existing patterns:
   - Models with SQLModel/SQLAlchemy  
   - Repository with BaseRepository pattern
   - Service with business logic + dependency injection
   - Router with FastAPI endpoints
2. Implement timezone-aware streak calculation service
3. Add idempotency middleware or decorator
4. Update habit service to include streak data  
5. Create Alembic migration for new tables
6. Update frontend to add logging UI and streak display
7. Regenerate OpenAPI client

**Acceptance criteria**

* Can log habit completion with automatic streak calculation
* Idempotency prevents duplicate logs for same date
* Streak calculation works correctly across timezones and DST
* Frontend shows real-time streak updates after logging
* All tests pass including new timezone/streak test cases

---

# Phase 3 — Reminder System with Background Jobs

**Objective:** Add reminder scheduling leveraging existing infrastructure and email service.

**Priority:** High
**Complexity:** Medium (leverage existing email service)

**Current assets to leverage:**
* ✅ Email service exists in `app/infrastructure/email/service.py`
* ✅ Redis available in docker-compose for job queue
* ✅ Email templates structure in `app/infrastructure/email/templates/`

**Deliverables**

* New `reminders` domain following existing patterns
* Background job system (using Celery or similar)
* Integration with existing email infrastructure
* Reminder management UI in frontend

**New Domain Structure**

```
app/domains/reminders/
├── __init__.py  
├── models.py          # Reminder model
├── schemas.py         # ReminderCreate, ReminderResponse
├── repository.py      # ReminderRepository
├── service.py         # ReminderService + scheduling logic
└── router.py          # Reminder CRUD endpoints

app/infrastructure/jobs/        # NEW
├── __init__.py
├── worker.py          # Celery worker setup
├── scheduler.py       # Periodic reminder scheduling
└── tasks.py           # Background job tasks
```

**DB model additions**

```sql
reminders (
  id uuid primary key,
  habit_id uuid references habits(id) on delete cascade,
  user_id uuid references user(id) on delete cascade,
  time_of_day time not null,     -- local time (20:45)
  enabled boolean default true,
  channel text default 'email', -- "email" (push later)
  created_at timestamptz default now(),
  updated_at timestamptz
);
```

**Integration with existing email service**

* Extend `app/infrastructure/email/service.py` with habit reminder methods
* Create new email template: `habit_reminder.mjml` 
* Reuse existing SMTP configuration and sending logic

**New API endpoints**

* `POST /api/v1/habits/{id}/reminders` - Create/update reminder
* `GET /api/v1/reminders` - List user's reminders  
* `PUT /api/v1/reminders/{id}` - Update reminder
* `DELETE /api/v1/reminders/{id}` - Delete reminder

**Tasks**

1. Create reminders domain following existing patterns
2. Add background job infrastructure (Celery + Redis)
3. Create habit reminder email template using existing MJML structure
4. Implement timezone-aware reminder scheduling
5. Add reminder management to user settings frontend
6. Update service container for reminder dependencies
7. Create migration and update API router

**Acceptance criteria**

* Users can create/edit reminders for their habits
* Reminders are sent at correct local time via email
* Background job system processes reminders reliably  
* Frontend provides intuitive reminder management interface

---

# Phase 4 — Analytics Dashboard & Data Export

**Objective:** Add analytics and export features leveraging existing patterns and infrastructure.

**Priority:** Medium
**Complexity:** Medium

**Deliverables**

* Analytics domain with habit performance metrics
* Calendar heatmap component for frontend
* CSV export functionality
* Enhanced dashboard with insights

**New Domain Structure**

```
app/domains/analytics/
├── __init__.py
├── models.py          # Analytics aggregation models (if needed)
├── schemas.py         # HeatmapResponse, SummaryResponse, ExportRequest
├── repository.py      # AnalyticsRepository (complex queries)
├── service.py         # AnalyticsService (calculations & caching)
└── router.py          # Analytics endpoints
```

**New API endpoints**

* `GET /api/v1/analytics/habits/{id}/heatmap` - Calendar heatmap data
* `GET /api/v1/analytics/habits/{id}/summary` - Completion stats
* `GET /api/v1/analytics/dashboard` - User dashboard overview
* `POST /api/v1/exports/habits/{id}/csv` - Generate CSV export

**Frontend enhancements**

* Add analytics tab to habit detail page
* Calendar heatmap component (using existing Chakra UI components)
* Summary cards showing completion rate, current streak, best days
* Export button with download functionality

**Implementation approach**

* Efficient queries using existing PostgreSQL with proper indexing
* Cache aggregated data in Redis for frequently accessed metrics  
* Leverage existing React components and styling patterns
* Follow existing repository/service patterns for data access

**Tasks**

1. Create analytics domain following established patterns
2. Implement efficient database queries for habit performance metrics
3. Add calendar heatmap component to frontend using existing design system
4. Create CSV export service with async processing
5. Add analytics tab to habit detail page
6. Update dashboard with habit overview cards
7. Add database indexes for analytics performance

**Acceptance criteria**

* Calendar heatmap displays habit completion accurately
* Summary metrics show correct completion rates and trends
* CSV export works for large date ranges without timeouts
* Analytics interface is responsive and follows existing design patterns

---

# Phase 5 — Polish & Production Readiness

**Objective:** Enhance the user experience and prepare for production deployment.

**Priority:** High
**Complexity:** Medium

**Deliverables**

* Enhanced UI/UX with polished habit management interface
* Data seeding and demo content for showcasing
* Performance optimizations and caching
* Basic real-time updates for immediate feedback

**Frontend enhancements**

* Improved habit creation flow with better schedule selection
* Quick-action buttons for habit logging from dashboard
* Progress indicators and motivational elements
* Mobile-responsive design improvements
* Loading states and error handling

**Backend optimizations**

* Add caching layer for frequently accessed data
* Optimize database queries with proper indexing  
* Add API rate limiting for production use
* Improve error handling and validation messages

**Tasks**

1. Polish frontend components with better UX patterns
2. Add data seeding script for demo purposes
3. Implement caching strategy for streaks and analytics
4. Add comprehensive error handling and user feedback
5. Create demo user accounts and sample habits
6. Add API documentation and usage examples
7. Optimize database performance with indexes

**Acceptance criteria**

* Application feels responsive and provides clear user feedback
* Demo showcases core functionality effectively
* API performance meets acceptable response times
* Error handling gracefully guides users to resolution

---

# Phase 6 — Deployment & Launch Preparation

**Objective:** Deploy the application to production and prepare for real user testing.

**Priority:** High  
**Complexity:** Medium

**Current infrastructure advantages:**
* ✅ Docker Compose setup ready for production
* ✅ GitHub Actions workflows for CI/CD
* ✅ Environment configuration with proper secrets management

**Deliverables**

* Production deployment using existing Docker infrastructure
* Monitoring and observability setup
* Backup and recovery procedures
* User onboarding flow and documentation

**Deployment approach**

* Leverage existing GitHub Actions for automated deployment
* Use managed PostgreSQL and Redis services for reliability
* Deploy via Docker containers to cloud platform (Railway, Render, or similar)
* Configure environment variables and secrets properly

**Tasks**

1. Configure production environment variables
2. Set up managed database services (PostgreSQL, Redis)
3. Deploy via GitHub Actions to cloud platform
4. Configure monitoring and alerting
5. Test end-to-end flows in production environment
6. Create user documentation and onboarding guide
7. Set up backup procedures for user data

**Acceptance criteria**

* Application is accessible and functional in production
* All core user flows work without errors
* Monitoring alerts on system issues
* Backup and recovery procedures are tested and documented

---

# Future Enhancements (Post-Launch)

**Optional features to consider after core functionality is solid:**

* **Social Features**: Friend challenges, shared habits, leaderboards
* **Advanced Analytics**: Habit correlations, optimal timing suggestions, trend analysis  
* **Mobile App**: React Native or PWA for better mobile experience
* **Integrations**: Calendar sync, fitness tracker integration, API for third-party apps
* **Gamification**: Badges, achievement system, streak rewards
* **Team Features**: Family/team habit tracking, shared goals

---

# Implementation Notes

**Following existing project patterns:**
* Use established domain-driven design approach
* Leverage existing repository and service patterns  
* Build on current authentication and user management
* Extend existing frontend components and styling
* Utilize current Docker and CI/CD infrastructure

**Key principles:**
* Maintain code quality and test coverage
* Follow existing architectural patterns consistently
* Prioritize user experience and data accuracy
* Keep timezone handling precise and tested
* Design for scalability from the start

---

# Cross-phase items & engineering practices (always-on)

* **Schema & migration discipline:** always write Alembic migrations, test rollback.
* **Idempotency:** use `Idempotency-Key` headers for all mutating endpoints that may be retried.
* **Feature flags:** use for reminders and push channels to avoid breaking users.
* **DB indices:** add indexes on `(habit_id, local_date)`, `user_id`, and `reminders next_run` to optimize queries.
* **Observability:** log structured events for `habit_logged`, `reminder_sent`, `streak_changed`.
* **Documentation:** maintain API docs and developer onboarding in repo.

---

# Acceptance checklist template (use per-phase)

* [ ] Unit tests written for new logic (esp. streak and timezone)
* [ ] Integration tests for API endpoints
* [ ] Migration added and verified on local DB
* [ ] Linting/formatting checks pass
* [ ] Manual QA flow executed (create habit → log → verify streak)
* [ ] Monitoring metric added and dashboard updated
* [ ] Feature flag added if feature impacts existing users

---

# Example commit & branch workflow (recommended)

* Branch naming: `feature/habit-logging`, `fix/reminder-dlq`
* Pull Request checklist: description, related issue, migration included, tests, reviewer
* Merge only after CI + review

---
