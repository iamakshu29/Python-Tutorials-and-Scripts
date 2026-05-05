# Personal Expense Tracker API

This project is a RESTful API built with **FastAPI** and **SQLAlchemy** (SQLite) to track and manage personal expenses. It was built as a foundational learning project to practice core API development concepts in Python.

## What I Implemented in this Project

1. **FastAPI Routing (CRUD Operations):**
   - Built a complete set of endpoints to Create, Read, Update, and Delete expenses.
   - Handled Path parameters (e.g., `/expenses/{id}`) and Query parameters (e.g., `/expenses/category?category=Food`).

2. **Database Modeling with SQLAlchemy:**
   - Created an `Expenses` model representing a database table.
   - Practiced using various column data types including `Integer`, `String`, `Float`, `Boolean`, and `Date`.
   - Used SQLAlchemy's built-in functions like `func.current_date()` for default values and `func.sum()` for data aggregation.
---
### DB Model (SQLAlchemy)
```
Expense
  id          -> Integer, primary key, auto-increment
  title       -> String  (e.g. "Groceries")
  amount      -> Float
  category    -> String  (e.g. "Food", "Travel", "Bills")
  date        -> Date
  paid        -> Boolean, default=False
```

3. **Data Validation with Pydantic:**
   - Created strictly typed schemas (`ExpenseCreate`, `ExpensePaid`) to validate incoming JSON requests.
   - Applied constraints using `Field()` (e.g., `min_length`, `gt`) to ensure bad data is rejected before it ever hits the database.
   - Implemented a dedicated schema for `PATCH` requests to allow partial updates (updating only the `paid` status).
---

### Pydantic Model
Same as `BookRequest`/`Todo` — validate the request body with `Field()` constraints:
- `amount` → `gt=0`
- `title` → `min_length=3`
- `category` → `min_length=2`

---

4. **Dependency Injection & Session Management:**
   - Used FastAPI's `Depends()` to yield database sessions (`SessionLocal`) for each request.
   - Handled database commits, rollbacks on errors, and safely closing connections.

5. **API Best Practices:**
   - Returned appropriate HTTP status codes (e.g., `201 Created`, `204 No Content`, `202 Accepted`).
   - Learned the critical importance of **Route Ordering** in FastAPI (ensuring static routes like `/expenses/summary` are defined before dynamic ones like `/expenses/{id}`).

## API Endpoints to build

| Method | Route | Description |
|--------|-------|-------------|
| **GET** | `/expenses` | Retrieve all expenses. |
| **GET** | `/expenses/{id}` | Retrieve a single expense by its ID. |
| **GET** | `/expenses/category` | Filter expenses by category using a query parameter. |
| **GET** | `/expenses/summary` | Calculate and return the total amount spent across all expenses. |
| **POST** | `/expenses` | Add a new expense to the database. |
| **PUT** | `/expenses/{id}` | Fully update an existing expense. |
| **PATCH**| `/expenses/{id}` | Partially update an expense (mark as paid/unpaid). |
| **DELETE**|`/expenses/{id}` | Delete an expense from the database. |


### What's new vs your ToDo project 
- **`/summary/` endpoint** — get the sum amount
- **`PATCH` with its own Pydantic schema** 
- **Float column** — `Column(Float)` in SQLAlchemy, you haven't used this yet
- **Filtering by a non-id field** — `.filter(Todos.category == category)` same `.filter()` you already know

Everything else is identical to what you've already done — good repetition to make it stick.

## Tech Stack
- **Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Server:** Uvicorn
