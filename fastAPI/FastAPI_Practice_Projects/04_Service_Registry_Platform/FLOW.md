# Project Flow — Service Registry Platform

## What This Project Does

A developer registers their microservice (e.g. `payment-api`) with this platform. The platform then automatically checks every 30 seconds if that service is alive, stores the result, and fires an alert if something goes down.

---

## Request Flow

### 1. User registers/logs in (`/auth`)
- Register creates a user with bcrypt-hashed password
- Login validates credentials, returns a JWT token
- Every other endpoint requires that token in the `Authorization` header

### 2. User registers a service (`POST /services`)
- Provides: name, team, environment, `health_url` (where to ping), optional `webhook_url` (where to send alerts)
- Stored in `services` table with `current_status = unknown`

### 3. Background poller runs continuously (`poller.py`)
- On app startup, an `asyncio` loop starts in the background
- Every 30 seconds it fetches all active services from DB
- For each service, it calls `health_service.py`

### 4. Health service does the actual check (`health_service.py`)
- Makes an HTTP GET to `service.health_url` using `httpx`
- If it gets back a 200 → status = `healthy`
- Anything else (timeout, 500, connection error) → status = `unhealthy`
- Saves the result (status, response time, status code) to `health_checks` table
- Compares new status to the old `service.current_status`
- If status **changed** → calls `webhook.py` to send an alert
- Caches the current status in Redis
- Updates `service.current_status` and `service.last_checked_at`

### 5. Webhook delivery (`webhook.py`)
- Only fires when status changes (healthy→unhealthy or back)
- Does an `httpx.post` to the `webhook_url` the developer registered
- Payload contains: service name, old status, new status, timestamp

### 6. Redis caching (`redis_client.py`)
- After every health check, result is written to Redis with a short TTL
- `/metrics` endpoint reads from Redis instead of hitting the DB every time
- Makes the metrics endpoint fast and DB-friendly

### 7. Reading data
- `GET /health/{service_id}/history` → queries `health_checks` table, returns last N records
- `GET /metrics` → reads Redis cache, formats output in Prometheus format (plain text)
- `GET /services/{id}` → returns current service config + `current_status` from DB

### 8. Admin routes (`/admin`)
- Admin users can see all services/users across the whole platform
- Can force-deactivate a service (stops polling for it)

---

## Data Flow Summary

```
Startup        → poller loop starts in background
User action    → JWT protected → service registered in DB
Poller         → httpx ping → result saved to health_checks table
                → status changed? → webhook fired to developer
                → result cached in Redis
User reads     → /health/history from DB, /metrics from Redis
```

---

## Implementation Order

Each step depends on the previous one:

1. `config.py` — pydantic-settings reads `.env` (DATABASE_URL, SECRET_KEY, REDIS_URL)
2. `main.py` — lifespan, router registration, starts poller on startup
3. `redis_client.py` — Redis connection, `get_status` / `set_status` helpers
4. `webhook.py` — `send_webhook(url, payload)` via httpx async POST
5. `health_service.py` — core logic: ping → save to DB → webhook if changed → cache in Redis
6. `poller.py` — asyncio loop every 30s, calls health_service for each active service

---

## Files Still To Implement

| File | Status | Purpose |
|---|---|---|
| `app/main.py` | Empty | Lifespan, routers, middleware |
| `app/config.py` | Empty | Pydantic-settings (.env loading) |
| `app/utils/redis_client.py` | Empty | Redis connection + get/set helpers |
| `app/utils/webhook.py` | Empty | httpx webhook delivery |
| `app/utils/poller.py` | Empty | asyncio 30s polling loop |
| `app/services/health_service.py` | Empty | Core health check + DB write + webhook + cache |
