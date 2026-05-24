# FastAPI Authentication Notes

## 1. OAuth2 Password Flow

### Main Components

- `OAuth2PasswordRequestForm` → receives username/password
- `OAuth2PasswordBearer` → extracts Bearer token from Authorization header
- JWT library → creates/verifies tokens

---

## OAuth2 Flow

```text
username/password
        ↓
server verifies
        ↓
server generates token
        ↓
client stores token
        ↓
client sends Bearer token later
```

### Authorization Header

```http
Authorization: Bearer <token>
```

---

## Minimal OAuth2 Example

```python
from fastapi import FastAPI, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    if (
        form_data.username == "admin"
        and form_data.password == "secret"
    ):
        return {
            "access_token": "my-token",
            "token_type": "bearer"
        }

    return {"error": "invalid credentials"}


@app.get("/protected")
async def protected(
    token: str = Depends(oauth2_scheme)
):

    return {"token": token}
```

---

## Important Notes

- `OAuth2PasswordRequestForm` only parses login form data.
- `OAuth2PasswordBearer` only extracts Bearer tokens.
- `OAuth2PasswordBearer` does NOT validate JWT automatically.
- Swagger shows lock icons because OAuth2PasswordBearer registers a security scheme.
- GET endpoints should not use OAuth2PasswordRequestForm.
- OAuth2 login endpoint should usually be POST.

---

# 2. HTTP Basic Authentication

## Main Components

- `HTTPBasic` → extracts Basic Authorization header
- `HTTPBasicCredentials` → contains username/password

---

## HTTP Basic Flow

```text
client sends username/password
on EVERY request
        ↓
browser/swagger may cache credentials
        ↓
server validates credentials each time
```

### Authorization Header

```http
Authorization: Basic base64(username:password)
```

---

## Minimal HTTP Basic Example

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials
)

app = FastAPI()

security = HTTPBasic()


@app.get("/protected")
async def protected(
    credentials: HTTPBasicCredentials = Depends(security)
):

    if (
        credentials.username != "admin"
        or credentials.password != "secret"
    ):
        raise HTTPException(status_code=401)

    return {"message": "authenticated"}
```

---

## Important Notes

- HTTP Basic does not use tokens.
- Username/password are sent repeatedly.
- Browser or Swagger may cache credentials.
- Server remains stateless.
- No login endpoint is usually needed.

---

# 3. OAuth2 vs HTTP Basic

| Feature | OAuth2 | HTTP Basic |
|---|---|---|
| Credential sent repeatedly | Token | Username/password |
| Login endpoint | Usually required | Usually not required |
| Uses tokens | Yes | No |
| Swagger lock support | Yes | Yes |
| More secure for APIs | Yes | Less |
| Typical header | Bearer token | Basic credentials |

---

# Important Concept Summary

## OAuth2PasswordRequestForm

Used only for:

```text
receiving username/password
```

It does NOT:

- authenticate future requests
- create sessions
- validate tokens

---

## OAuth2PasswordBearer

Used for:

```text
extracting Bearer token
```

It also:

- enables Swagger lock icons
- adds OAuth2 schema to OpenAPI
- integrates Authorize button

---

## Why HTTPBasic Feels Logged In

Browser/Swagger automatically reuses:

```http
Authorization: Basic ...
```

on later requests.

Server itself is still stateless.
