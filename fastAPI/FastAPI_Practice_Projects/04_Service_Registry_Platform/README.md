# Service Registry & Health Monitoring Platform

A Platform Engineering API built with FastAPI. Engineers register their microservices, the platform periodically checks if they're alive, caches results in Redis, and fires webhook alerts when a service goes down or recovers.

> **Portfolio project** — built to demonstrate platform engineering skills: REST API design, background task scheduling, Redis caching, webhook delivery, JWT auth, and Prometheus-compatible metrics.

---

## The Problem It Solves

In a company with many microservices, you need to know:
- Which services exist, who owns them, and what environment they're in
- Whether they're currently healthy
- When they go down — before users notice

This platform provides a programmable API layer for all of that. It complements tools like Prometheus/Grafana by acting as the **service registry and alert dispatcher**.

---

## How It Works (Simple Flow)

```
Developer registers service → Platform stores it in DB
         ↓
Background poller hits /health every 30s
         ↓
Result cached in Redis (fast reads)
         ↓
Status changed? → Fire webhook to developer's Slack/Teams URL
         ↓
All statuses exposed at /metrics (Prometheus format)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (SQLAlchemy ORM) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (jose) + bcrypt |
| Caching | Redis (`redis-py`) |
| HTTP Client | httpx (async) |
| Background Tasks | FastAPI `BackgroundTasks` + `asyncio` |
| Containerization | Docker + Docker Compose |
| Testing | pytest + TestClient |

---

## Database Models

### User
Who can register and manage services.

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| email | String | Unique |
| username | String | Unique |
| hashed_password | String | bcrypt hashed |
| role | Enum | `admin` or `user` |
| created_at | DateTime | Auto set |

### Service
A registered microservice being monitored.

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | String | Unique, e.g. `payment-api` |
| team | String | Owning team name |
| environment | Enum | `dev`, `staging`, `prod` |
| health_url | String | URL the poller hits e.g. `http://svc/health` |
| webhook_url | String | Nullable — where to POST alerts |
| current_status | Enum | `healthy`, `unhealthy`, `unknown` |
| is_active | Boolean | If false, polling stops |
| registered_by | UUID | FK → users.id |
| created_at | DateTime | Auto set |
| last_checked_at | DateTime | Updated each poll |

### HealthCheck
History of every poll result.

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| service_id | UUID | FK → services.id |
| status | Enum | `healthy` or `unhealthy` |
| response_time_ms | Integer | How long the health call took |
| status_code | Integer | HTTP status returned |
| error_detail | String | Nullable — e.g. `"Connection refused"` |
| checked_at | DateTime | Auto set |

---

## API Endpoints

### Auth — `/auth`

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login, get JWT token | No |
| GET | `/auth/me` | Get current user info | Yes |

### Services — `/services`

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/services` | Register a new service | Yes |
| GET | `/services` | List your services | Yes |
| GET | `/services/{id}` | Get service details + current status | Yes |
| PATCH | `/services/{id}` | Update service config | Yes (owner) |
| DELETE | `/services/{id}` | Deregister a service | Yes (owner) |
| POST | `/services/{id}/check` | Manually trigger a health check now | Yes |

### Health History — `/health`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/health/{service_id}/history` | Last N poll results for a service | Yes |

### Metrics — `/metrics`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/metrics` | Prometheus-format status of all services | No |

### Admin — `/admin`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/admin/services` | All services across all users | Admin |
| GET | `/admin/users` | All registered users | Admin |
| PATCH | `/admin/services/{id}/deactivate` | Force-deactivate a service | Admin |

---

## Project Structure

```
04_Service_Registry_Platform/
├── app/
│   ├── main.py              # App entry point, lifespan, router registration
│   ├── database.py          # SQLAlchemy engine + session
│   ├── config.py            # Settings via pydantic-settings (.env loading)
│   ├── dependencies.py      # get_db, get_current_user, require_admin
│   ├── models/
│   │   ├── user.py          # User SQLAlchemy model
│   │   ├── service.py       # Service SQLAlchemy model
│   │   └── health_check.py  # HealthCheck SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py          # Pydantic schemas for User
│   │   ├── service.py       # Pydantic schemas for Service
│   │   └── health_check.py  # Pydantic schemas for HealthCheck
│   ├── routers/
│   │   ├── auth.py          # /auth routes
│   │   ├── services.py      # /services routes
│   │   ├── health.py        # /health routes
│   │   ├── metrics.py       # /metrics route (Prometheus format)
│   │   └── admin.py         # /admin routes
│   ├── services/
│   │   └── health_service.py  # Core polling logic, webhook firing
│   └── utils/
│       ├── auth.py          # JWT create/decode, bcrypt helpers
|       ├── logger.py        # For JSON Structured Log Configuration
│       ├── poller.py        # Background polling loop (asyncio)
│       ├── webhook.py       # Send POST to webhook URLs (httpx)
│       └── redis_client.py  # Redis connection + get/set helpers
├── alembic/                 # DB migration files
├── tests/
│   ├── conftest.py          # DB setup, test client, fixtures
│   ├── test_auth.py
│   ├── test_services.py
│   └── test_health.py
├── .env.example             # Template — copy to .env
├── docker-compose.yml       # API + PostgreSQL + Redis
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── pytest.ini
```

---

## Key Concepts This Project Covers

| Concept | Where |
|---|---|
| JWT Auth + bcrypt | `utils/auth.py`, `/auth` router |
| Role-based access (admin vs user) | `dependencies.py` |
| SQLAlchemy ORM (modern `Mapped` style) | `models/` |
| Pydantic v2 schemas | `schemas/` |
| Alembic migrations | `alembic/` |
| Redis caching | `utils/redis_client.py` |
| Async background polling | `utils/poller.py` |
| Webhook delivery | `utils/webhook.py` |
| Prometheus metrics format | `routers/metrics.py` |
| Docker multi-service setup | `docker-compose.yml` |
| pytest fixtures + DB override | `tests/conftest.py` |

---

## Potential Improvements (Not Yet Implemented)

- Rate limiting per user using `slowapi`
- Retry logic on webhook delivery failures
- WebSocket live feed of health status changes
- Slack/Teams integration (pre-built webhook templates)
- Dashboard UI
