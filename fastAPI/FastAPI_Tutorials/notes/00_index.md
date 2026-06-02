# FastAPI — Concept Notes Index

<!-- Reference index for all concept notes in this folder -->
<!-- Stack: FastAPI 0.115 | SQLAlchemy 2.0 | Pydantic v2 | Python 3.12 -->

---

## Notes in this folder

| File | Covers |
|---|---|
| [01_app_structure_and_routers.md](01_app_structure_and_routers.md) | `main.py`, `APIRouter`, `include_router`, sharing deps across routers |
| [02_database_setup_and_models.md](02_database_setup_and_models.md) | `database.py`, `get_db`, SQLAlchemy models (modern `Mapped` style), Enum columns |
| [03_pydantic_schemas.md](03_pydantic_schemas.md) | Request/response schemas, `ConfigDict`, `from_attributes`, partial update (PATCH) |
| [04_dependency_injection.md](04_dependency_injection.md) | `Depends()`, `yield` vs `return`, chained deps, `Annotated` pattern, RBAC |
| [05_authentication_jwt.md](05_authentication_jwt.md) | bcrypt, JWT create/decode, `OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`, Google OAuth difference |
| [06_error_handling.md](06_error_handling.md) | 4-layer pattern, `try/except` vs `if/raise`, status codes, `Path`/`Query` validation |
| [07_alembic_migrations.md](07_alembic_migrations.md) | `alembic init`, `revision`, `upgrade`, `downgrade`, autogenerate limitations |
| [08_testing.md](08_testing.md) | `TestClient`, `conftest.py`, DB override, auth override, test naming |
| [09_sqlalchemy_queries.md](09_sqlalchemy_queries.md) | `select()` style (2.x), `scalar_one_or_none`, filter operators, `flush` vs `commit` |

---

## Modern Syntax Quick Reference (Ruff-clean)

### SQLAlchemy Model
```python
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
class Base(DeclarativeBase): pass
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str | None] = mapped_column(nullable=True)
```

### Pydantic Schema
```python
from pydantic import BaseModel, ConfigDict
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
```

### Query
```python
from sqlalchemy import select
result = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
```

---

## Things I Keep Getting Wrong

- `algorithms=[ALGORITHM]` is a **list** in `jwt.decode()`, not a string.
- `OAuth2PasswordRequestForm` needs **form data** (not JSON) + `python-multipart` installed.
- `from_attributes=True` is Pydantic v2. `orm_mode = True` is v1 (avoid).
- `declarative_base()` is deprecated — use `class Base(DeclarativeBase): pass`.
- `401` = not authenticated. `403` = authenticated but no permission. Don't mix them.
- `db.commit()` in `get_db` means don't call `db.commit()` inside individual routes.
- `datetime.now(timezone.utc)` not `datetime.utcnow()` (deprecated Python 3.12+).
