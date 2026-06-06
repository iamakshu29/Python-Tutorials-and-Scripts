# URL Shortener API

A RESTful URL shortening service built with Python and FastAPI. Converts long URLs into short, shareable links and tracks redirect analytics, complete with user authentication and subscription tiers.

> **Portfolio project** — built as part of a backend engineering learning path, focusing on REST API design, database integration, authentication, and deployment fundamentals.

---

## Features

- User Authentication via HTTP Basic Auth
- User Roles and Subscription Tiers (Basic/Premium)
- Shorten any valid URL to a compact alias
- Custom alias support (optional)
- Click tracking and analytics per short URL
- Expiry support for time-limited links with manual upgrade/renewal
- JSON-based REST API

---

## Tech Stack

| Layer            | Technology                        |
| ------------------| -----------------------------------|
| Language         | Python 3.11+                      |
| Framework        | FastAPI                           |
| Database         | PostgreSQL (via SQLAlchemy ORM)   |
| Migrations       | Alembic                           |
| Validation       | Pydantic v2                       |
| Security         | passlib (bcrypt), HTTP Basic Auth |
| Server           | Uvicorn                           |
| Containerization | Docker + Docker Compose           |
| Testing          | Pytest                            |

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py            # App entry point, router registration
│   ├── config.py          # Environment config via Pydantic Settings
│   ├── database.py        # SQLAlchemy engine and session setup
│   ├── models/            # SQLAlchemy ORM models (User, URL)
│   ├── schemas/           # Pydantic request/response schemas
│   ├── utils/             # Helpers (auth, aliases, db_session)
│   ├── crud.py            # DB operations
│   └── routers/
│       ├── urls.py        # URL operations (create, read, renew)
│       ├── stats.py       # URL stats and tracking
│       ├── user.py        # User management and authentication
│       └── admin.py       # Admin-specific routes
├── alembic/               # DB migration files
├── tests/
│   ├── test_urls.py
│   └── test_stats.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## API Endpoints

*Note: Most endpoints require HTTP Basic Authentication.*

### Admin Endpoints (`/admin`)

- `GET /admin/user` - List all users (Requires Admin role).
- `GET /admin/url` - List all urls (Requires Admin role).
- `DELETE /admin/{alias}` - Delete a short URL (Requires Admin role).

### User Endpoints (`/user`)

- `POST /user/` - Create a new user (Requires email, username, password, and role).
- `GET /user/` - Get details of the currently logged-in user.
- `PATCH /user/upgrade?subscription=Premium` - Upgrade user subscription.

### URL Endpoints (`/url`)

- `POST /url/` - Create a short URL. Optional custom `urlCode` and `expires_in` (minutes).
- `GET /url/` - Get all shortened URLs created by the authenticated user.
- `GET /url/{alias}` - Retrieve details of a specific URL by its alias.
- `PATCH /url/upgrade/{alias}` - Upgrade/renew an expired URL. Extends expiry time or generates a new alias depending on subscription tier.

### Stats Endpoints (`/stats`)

- `GET /stats/{alias}` - Access a short URL, increment its click count, and return its details (Simulates redirection/analytics access).

### Redirect Endpoints (`/redirect`)

- `GET /redirect/{alias}` - Redirect the URL with the short_url.

---

## Database Models

### User

| Column            | Type     | Notes                       |
| -------------------| ----------| -----------------------------|
| id                | UUID     | Primary key, auto-generated |
| email             | String   | Unique, indexed             |
| username          | String   | Unique, indexed             |
| hashed_password   | String   | bcrypt hashed               |
| role              | Enum     | `Admin` or `User`           |
| subscription_type | Enum     | `Basic` or `Premium`        |
| is_active         | Boolean  | Default `True`              |
| created_at        | DateTime | Auto set on insert          |

### URL

| Column | Type | Notes |
|---|---|---|
| urlCode | String | Primary key, alias for the short URL |
| original_url | String | The full destination URL |
| click_count | Integer | Default `0`, incremented on each access |
| created_at | DateTime | Auto set on insert |
| expires_at | DateTime | Expiry time (7 min for Basic, 70 min for Premium) |
| last_accessed_at | DateTime | Updated on each redirect |
| user_id | UUID | FK → User.id |

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL running locally, or use Docker Compose (recommended)
- `pip` or a virtual environment manager

### 1. Clone the repository

```bash
git clone https://github.com/your-username/url-shortener.git
cd url-shortener
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/urlshortener
BASE_URL=http://localhost:8000
SECRET_KEY=your-secret-key
```

### 3. Run with Docker Compose (recommended)

```bash
docker-compose up --build
```

This starts both the API server and PostgreSQL. The API will be available at `http://localhost:8000`.

### 4. Run locally without Docker

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Note: You may need to run this from inside the app/ directory depending on your setup
# pip install -r app/requirements.txt

# Apply DB migrations
alembic upgrade head

# Start the server (from the app directory)
cd app
uvicorn main:app --reload
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database — no external services required.

---

## Key Concepts Practiced

This project was intentionally built to get hands-on with specific backend engineering fundamentals:

- **REST API design** — resource-oriented routes, correct HTTP status codes (`201`, `302`, `404`, `410`)
- **Authentication & Authorization** — implementing HTTP Basic Auth and role-based access control.
- **ORM usage** — SQLAlchemy models, relationships, and query patterns
- **Schema validation** — separating DB models from API schemas using Pydantic
- **Database migrations** — Alembic for versioned, repeatable schema changes
- **Environment config management** — 12-factor app config via `.env` and Pydantic Settings
- **Containerization** — multi-service Docker Compose setup with health checks
- **Error handling** — FastAPI `HTTPException` with descriptive error responses
- **Logging** - JSON Based Logging

---

## Potential Improvements (Not Yet Implemented)

- Real URL Redirection (Currently handled as a data response instead of `302 Found`)
- Redis caching for high-frequency redirects
- Advanced Analytics dashboard (click trends, referrers)
- QR code generation per short URL

---

## License

MIT