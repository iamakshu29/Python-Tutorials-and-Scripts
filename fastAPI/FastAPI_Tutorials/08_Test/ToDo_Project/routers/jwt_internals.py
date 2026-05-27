# =============================================================
# jwt_internals.py -- HOW JWT WORKS INTERNALLY (Reference Only)
# =============================================================
# This file is NOT part of the running application.
# It is kept here purely to understand what a JWT library (like python-jose) does under the hood.
#
# In real projects, NEVER build JWT manually like this. Use python-jose:
#   pip install python-jose
#
#   from jose import jwt
#   token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")   # create token
#   data  = jwt.decode(token,  SECRET_KEY, algorithms=["HS256"]) # verify + decode token
#
# python-jose handles all of the steps below for you safely and correctly.
# =============================================================

import base64
import hmac
import hashlib
import json
from datetime import datetime


# =============================================================
# WHAT IS A JWT?
# =============================================================
# JWT (JSON Web Token) is a compact, URL-safe string used to securely transfer claims
# (data) between two parties - typically a client and a server.
#
# Structure: base64url(HEADER) . base64url(PAYLOAD) . base64url(SIGNATURE)
#
#   HEADER    -> tells the receiver which algorithm was used to sign this token
#   PAYLOAD   -> the actual data (claims): user info, roles, expiry time, etc.
#   SIGNATURE -> proves the token was not tampered with; only valid if signed with the correct secret
#
# Important:
#   - The header and payload are only BASE64 ENCODED, not encrypted.
#     Anyone who intercepts the token CAN decode and read the payload.
#   - The signature guarantees INTEGRITY (not modified), not SECRECY (data is not hidden).
#   - Never put sensitive data (raw passwords, card numbers) in a JWT payload.


# =============================================================
# STEP-BY-STEP: Manual JWT Construction
# =============================================================

def create_JWT_manual(username: str, user_id: int, role: str) -> str:
    """
    Manually builds a JWT token step by step.
    This is exactly what jwt.encode() inside python-jose does internally.
    """

    # ----------------------------------------------------------
    # STEP 1: Build the Header
    # ----------------------------------------------------------
    # The header declares:
    #   "alg" -> which algorithm signs the token (HS256 = HMAC + SHA256)
    #   "typ" -> the token type (always "JWT" for JWTs)
    JWT_header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    # ----------------------------------------------------------
    # STEP 2: Build the Payload (Claims)
    # ----------------------------------------------------------
    # Claims are key-value pairs that carry information about the user.
    #
    # Standard registered claims (from RFC 7519):
    #   "sub" (subject)  -> who the token is about (use stable id like user_id, not timestamp)
    #   "exp" (expiry)   -> Unix timestamp after which the token is invalid (checked by jose on decode)
    #   "iat" (issued at)-> when the token was created
    #
    # Custom claims (you define these - anything your app needs):
    #   "id", "role"     -> added here so routes can use them without hitting the DB on every request
    JWT_payload = {
        "sub": username,                # subject: the username
        "id": user_id,                  # custom: DB user id
        "role": role,                   # custom: "admin" or "user"
        "iat": str(datetime.utcnow()),  # issued at (informational)
        # "exp": ... would go here in production - python-jose checks this automatically on decode
    }

    # ----------------------------------------------------------
    # STEP 3: Serialize to compact JSON (no whitespace)
    # ----------------------------------------------------------
    # separators=(",", ":") removes all spaces from the JSON string
    # smaller string = smaller token = less data sent on every HTTP request
    # .encode() converts the Python string to bytes (required for base64 and hmac)
    header_json  = json.dumps(JWT_header,  separators=(",", ":")).encode()
    payload_json = json.dumps(JWT_payload, separators=(",", ":")).encode()

    # ----------------------------------------------------------
    # STEP 4: Base64URL Encode the Header and Payload
    # ----------------------------------------------------------
    # Base64URL is Base64 with two character substitutions:
    #   "+" -> "-"    "/" -> "_"    and padding "=" is stripped
    # This makes the token safe to embed in URLs and HTTP headers without escaping.
    #
    # rstrip(b"=") removes the "=" padding characters (JWT spec does not use them)
    header_b64  = base64.urlsafe_b64encode(header_json).rstrip(b"=")
    payload_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b"=")

    # ----------------------------------------------------------
    # STEP 5: Create the Signing Input
    # ----------------------------------------------------------
    # The signing input is: base64url(header) + "." + base64url(payload)
    # This is the exact string that gets cryptographically signed in the next step.
    # If ANYONE modifies even one character in the header or payload,
    # the signing input changes -> the recomputed signature won't match -> token rejected.
    message = header_b64 + b"." + payload_b64

    # ----------------------------------------------------------
    # STEP 6: Sign with HMAC-SHA256
    # ----------------------------------------------------------
    # HMAC (Hash-based Message Authentication Code):
    #   - combines the secret key + the message using SHA256 hashing
    #   - produces a fixed 32-byte signature that is unique to THIS message + THIS secret
    #   - without the secret, nobody can reproduce the same signature -> cannot forge the token
    #
    # .digest() returns raw bytes of the signature
    #
    # In production: load the secret from an environment variable, NEVER hardcode it
    secret = b"learningapi"
    signature = hmac.new(secret, message, hashlib.sha256).digest()

    # ----------------------------------------------------------
    # STEP 7: Base64URL Encode the Signature
    # ----------------------------------------------------------
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=")

    # ----------------------------------------------------------
    # STEP 8: Assemble the Final JWT
    # ----------------------------------------------------------
    # Format: base64url(header) . base64url(payload) . base64url(signature)
    # .decode() converts the bytes result back to a regular Python string
    jwt_token = (message + b"." + signature_b64).decode()

    return jwt_token


# =============================================================
# HOW VERIFICATION WORKS (when the server receives a token back from the client)
# =============================================================
# The server receives: header_b64 . payload_b64 . signature_b64
#
# 1. Split on "." -> extract the three parts
# 2. Re-create the signing input: header_b64 + "." + payload_b64
# 3. Sign it again with the SAME secret key using HMAC-SHA256
# 4. Compare the re-computed signature with signature_b64 from the token
# 5. If they MATCH    -> token is authentic and untampered -> trust the payload
# 6. If they MISMATCH -> token was modified or signed with a different secret -> REJECT (401)
# 7. Also check "exp" claim -> if current time > exp -> REJECT (401, token expired)
#
# python-jose does ALL of this in one call:
#   payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#   raises JWTError automatically if invalid, expired, tampered, or wrong algorithm