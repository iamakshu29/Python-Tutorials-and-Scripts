Viewed Application.py:47-66

Great question! Here is the full chain of events that led to this error:

### Step 1 — Your original enums were fine
Your original code in `schemas/ApplicationCreate.py` (before our refactoring) had:
```python
class StatusEnum(str, Enum):
    applied = "Applied"   # name=applied, value=Applied
```
Notice the **member name is lowercase** (`applied`). SQLAlchemy by default stores the **name** → so it stored `"applied"` in the DB. The PostgreSQL enum was also created with `"applied"`, so everything matched!

### Step 2 — The refactoring broke it
When I consolidated the enums and moved them into `models/User.py` and `models/Application.py`, the new enums were written with **UPPERCASE member names**:
```python
class UserRole(str, Enum):
    ADMIN = "Admin"   # name=ADMIN, value=Admin
    USER = "User"
```

### Step 3 — SQLAlchemy's default behaviour
By default, `SQLAlchemy`'s `SQLEnum` stores the Python **member name** (the left side, `ADMIN`) into the database column, **not the value** (`Admin`). 

So now SQLAlchemy was sending `"ADMIN"` to PostgreSQL, but your database column was a PostgreSQL native `ENUM` type that was created with valid values of `"Admin"` and `"User"`.

PostgreSQL received `"ADMIN"`, checked its list of valid values (`Admin`, `User`), couldn't find a match, and threw:
```
invalid input value for enum user_role: "ADMIN"
```

### The Root Cause in One Line
> **The original enums used lowercase names, so the name and value stored were both lowercase. The new enums used UPPERCASE names, which SQLAlchemy stored as-is, mismatching the database values.**

The `values_callable` fix forces SQLAlchemy to always use the **`.value`** (right side) regardless of what the **`.name`** (left side) is, making it immune to this confusion in the future!