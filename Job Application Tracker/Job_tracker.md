# Job Application Tracker API — Full Project Overview

---

## What It Does

A REST API where users track their job applications. Each user manages their own applications. Admin users can view aggregate data across all users. The system supports two login methods: email/password and Google OAuth.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (jose) + bcrypt + OAuth2 |
| Google Login | Google OAuth2 (requests) |
| Rate Limiting | slowapi | Pagination
| Logging (JSON format) |
| Testing | pytest + httpx (TestClient) |
| Containerization | Docker + docker-compose |

---

## Project Structure

```
job_tracker/
├── app/
│   ├── main.py                  # App entry point, middleware, router registration
│   ├── config.py                # Settings via pydantic-settings (.env loading)
│   ├── database.py              # SQLAlchemy engine + session
│   ├── dependencies.py          # Reusable FastAPI dependencies (get_db, get_current_user)
│   │
│   ├── models/
│   │   ├── user.py              # User SQLAlchemy model
│   │   └── application.py      # Application SQLAlchemy model
│   │
│   ├── schemas/
│   │   ├── user.py              # Pydantic schemas for User
│   │   └── application.py      # Pydantic schemas for Application
│   │
│   ├── routers/
│   │   ├── auth.py              # /auth — register, login, google-login
│   │   ├── applications.py      # /applications — CRUD
│   │   └── admin.py             # /admin — aggregate views
│   │
│   ├── services/
│   │   ├── auth_service.py      # Password hashing, JWT creation/decode
│   │   └── google_oauth.py      # Google token exchange + user info fetch
│   │
│   └── utils/
│       ├── logger.py            # JSON structured logger setup
│       └── rate_limit.py        # slowapi limiter instance
│
├── alembic/
│   ├── env.py
│   └── versions/               # Migration files live here
│
├── tests/
│   ├── conftest.py              # DB setup, test client, fixtures
│   ├── test_auth.py
│   ├── test_applications.py
│   └── test_admin.py
│
├── .env                         # Secrets (never commit)
├── .env.example                 # Template to commit
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Database Models

### User

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| email | String | Unique | indexed |
| hashed_password | String | Nullable (Google users have no password) |
| google_id | String | Nullable, unique |
| role | Enum | `user` or `admin` |
| is_active | Boolean | Default true |
| created_at | DateTime | Auto set |

### Application

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | FK → User.id |
| company | String | Required |
| role_title | String | Required |
| job_url | String | Optional |
| status | Enum | `applied`, `interview`, `offer`, `rejected`, `ghosted` |
| applied_date | Date | Required |
| notes | Text | Optional |
| created_at | DateTime | Auto set |
| updated_at | DateTime | Auto updated |

---

## API Endpoints

### Auth — `/auth`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register with email + password | No |
| POST | `/auth/login` | Login, returns JWT | No |
| GET | `/auth/google` | Redirect to Google consent screen | No |
| GET | `/auth/google/callback` | Handle Google OAuth callback, return JWT | No |
| GET | `/auth/me` | Return current user info | Yes |

### Applications — `/applications`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | `/applications` | Create new application | Yes |
| GET | `/applications` | List own applications (paginated, filtered, sorted) | Yes |
| GET | `/applications/{id}` | Get single application | Yes (owner only) |
| PUT | `/applications/{id}` | Update application | Yes (owner only) |
| DELETE | `/applications/{id}` | Delete application | Yes (owner only) |

**Query params for GET /applications:**
- `status` — filter by status enum
- `company` — partial match filter
- `sort_by` — `applied_date`, `created_at`, `company` (default: `created_at`)
- `order` — `asc` or `desc` (default: `desc`)
- `page` — page number (default: 1)
- `limit` — items per page (default: 10, max: 50)

### Admin — `/admin`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | `/admin/users` | List all users | Admin only |
| GET | `/admin/applications` | List all applications across users | Admin only |
| GET | `/admin/stats` | Aggregate stats (total apps, status breakdown, top companies) | Admin only |

---

## Auth Flow

### Email/Password
1. User registers → password hashed with bcrypt → stored
2. User logs in → password verified → JWT returned (expires in 20 min)
3. Protected routes → `OAuth2PasswordBearer` extracts token → `jose` decodes → user fetched from DB

### Google OAuth
1. User hits `/auth/google` → redirected to Google consent screen
2. Google redirects to `/auth/google/callback?code=...`
3. Backend exchanges code for access token using `requests` (with retry logic)
4. Backend fetches user info from Google API
5. If user exists (by google_id or email) → return JWT. If not → create user → return JWT

### Role-Based Access
- Dependency `get_current_user` validates token and returns user object
- Dependency `require_admin` checks `user.role == "admin"`, raises 403 if not
- Owner check on application endpoints: `application.user_id != current_user.id` → 403

---

## Key Implementation Details

### Retry Logic (Google API calls)
```python
# In google_oauth.py — use requests with manual retry
import time

def fetch_google_user_info(access_token: str, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # exponential backoff
```

### JWT Token
```python
# In auth_service.py
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Pagination Pattern
```python
# Consistent pattern used in applications router
def paginate(query, page: int, limit: int):
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": ceil(total / limit),
        "items": items
    }
```

### JSON Logging
```python
# In utils/logger.py
import logging, json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "timestamp": self.formatTime(record),
        })
```

### Rate Limiting
```python
# In utils/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# In router
@router.post("/applications")
@limiter.limit("20/hour")
async def create_application(request: Request, ...):
    ...
```

---

## Alembic Migrations — Planned Sequence

| Migration | What it does |
|---|---|
| `001_create_users` | Create users table |
| `002_create_applications` | Create applications table with FK |
| `003_add_notes_column` | Add `notes` column to applications (simulate real-world schema change) |

The third migration is intentional — it teaches you what happens when you need to alter a live table.

---

## Pydantic Schemas

### ApplicationCreate
```python
class ApplicationCreate(BaseModel):
    company: str
    role_title: str
    job_url: Optional[HttpUrl] = None
    status: ApplicationStatus = ApplicationStatus.applied
    applied_date: date
    notes: Optional[str] = None
```

### ApplicationResponse
```python
class ApplicationResponse(ApplicationCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## Environment Variables (.env.example)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/job_tracker
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

---

## Docker Setup

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: job_tracker
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing Strategy

### What to test

| Test File | What it covers |
|---|---|
| `test_auth.py` | Register, login, invalid password, token expiry, Google callback mock |
| `test_applications.py` | CRUD, owner-only access, pagination params, filter/sort |
| `test_admin.py` | Admin-only access, 403 for regular users, stats accuracy |

### Test Setup Pattern
```python
# conftest.py — use a separate test DB, override dependency
@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
```

---

## Build Order (Recommended)

1. Project structure + config + database connection
2. User model + Alembic migration 001
3. Register + login endpoints (email/password only)
4. JWT creation and `get_current_user` dependency
5. Application model + migration 002
6. Application CRUD endpoints (no filtering yet)
7. Add pagination + filtering + sorting
8. Role-based access + admin routes
9. Google OAuth integration
10. Migration 003 (add notes column)
11. Rate limiting
12. JSON logging
13. Tests
14. Dockerize

---

## What This Covers From Your Skillset

| Your Skill | Where Applied |
|---|---|
| requests + retry logic | Google user info fetch |
| Google OAuth setup | `/auth/google` flow |
| Error handling | HTTPException, RequestException, JWTError |
| Classes + OOP | Services, SQLAlchemy models |
| Decorators | `@limiter.limit`, `@router.get`, custom deps |
| Static typing | All function signatures, Pydantic schemas |
| FastAPI routes + routers | 3 separate routers with prefixes |
| DB connection | SQLAlchemy + session management |
| Pydantic validation | All request/response schemas |
| Alembic migrations | 3 planned migrations |
| bcrypt | Password hashing/verification |
| JWT (jose) | Token creation and decoding |
| OAuth2PasswordBearer | Token extraction from headers |
| Role-based access | Admin vs user dependency |
| Pagination/filter/sort | Applications list endpoint |
| JSON logging | All auth events + external calls |
| Rate limiting | POST /applications |
| Testing | Auth + CRUD + admin coverage |
| Project structure | Feature-based folder layout |
| Docker | Full docker-compose setup |