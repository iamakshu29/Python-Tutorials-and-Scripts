# jwt_utils.py -- HOW JWT WORKS INTERNALLY (Educational Reference)
# =============================================
# This file exists purely to understand the internals of JWT construction from scratch.
# In real projects, NEVER do this manually. Use python-jose instead:
#
#   pip install python-jose
#
#   from jose import jwt
#   token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#   data   = jwt.decode(token,  SECRET_KEY, algorithms=["HS256"])
#
# python-jose handles: Base64URL encoding, signing, expiry validation,
#                      algorithm flexibility, and security edge cases for you.
# =============================================

import base64
import hmac
import hashlib
import json
from datetime import datetime


# =============================================
# WHAT IS A JWT?
# =============================================
# JWT (JSON Web Token) is a compact, URL-safe way to represent claims (data) between two parties.
# It has 3 parts separated by dots:
#
#   base64url(HEADER) . base64url(PAYLOAD) . base64url(SIGNATURE)
#
# HEADER   - metadata: which algorithm was used to sign this token
# PAYLOAD  - the actual data (claims): user info, roles, expiry time, etc.
# SIGNATURE - proves the token wasn't tampered with; only verifiable with the secret key
#
# Anyone can DECODE the header and payload (they are just base64, not encrypted).
# But no one can FORGE a valid signature without the secret key.
# So JWT is about INTEGRITY (wasn't modified), not SECRECY (the data isn't hidden).


def create_JWT_manual(user) -> str:
    """
    Manually constructs a JWT token step by step.
    'user' should be a User SQLAlchemy model instance.

    This is how python-jose (and every JWT library) works under the hood.
    """

    # =============================================
    # STEP 1: Build the Header
    # =============================================
    # The header tells the receiver which algorithm was used to create the signature.
    # "alg": "HS256" -> HMAC with SHA-256
    # "typ": "JWT"   -> token type
    JWT_header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    # =============================================
    # STEP 2: Build the Payload (Claims)
    # =============================================
    # Claims are statements about the user and any additional metadata.
    # Standard registered claims (defined by JWT spec / RFC 7519):
    #   "sub" (subject)  -> who the token is about (usually user id, not timestamp - see note below)
    #   "iat" (issued at)-> when the token was created
    #   "exp" (expiry)   -> when the token expires (after this, token is invalid)
    # Custom claims (you define these):
    #   "name", "email", "admin" -> anything useful for your app
    #
    # NOTE: using datetime.utcnow() as "sub" is non-standard (done here for learning).
    #       In production, "sub" should be a stable unique identifier like the user's DB id.
    JWT_payload = {
        "sub": str(datetime.utcnow()),          # subject (replace with user.id in production)
        "name": user.first_name + " " + user.last_name,
        "given_name": user.first_name,
        "family_name": user.last_name,
        "email": user.email,
        "admin": user.role == "admin"           # True if admin, False otherwise
    }

    # =============================================
    # STEP 3: Serialize to JSON (compact, no spaces)
    # =============================================
    # separators=(",", ":") removes all whitespace from the JSON output
    # this keeps the token as small as possible (important since JWTs are sent in every request)
    # .encode() converts the string to bytes (required for base64 and hmac operations)
    header_json  = json.dumps(JWT_header,  separators=(",", ":")).encode()
    payload_json = json.dumps(JWT_payload, separators=(",", ":")).encode()

    # =============================================
    # STEP 4: Base64URL Encode Header and Payload
    # =============================================
    # Base64URL is similar to regular Base64 but:
    #   uses  "-" instead of "+"
    #   uses  "_" instead of "/"
    #   strips "=" padding (JWT spec doesn't use it)
    # This makes the token safe to use in URLs and HTTP headers without escaping.
    header_b64  = base64.urlsafe_b64encode(header_json).rstrip(b"=")
    payload_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b"=")

    # =============================================
    # STEP 5: Create the Signing Input
    # =============================================
    # The signing input is: base64url(header) + "." + base64url(payload)
    # This is the exact string that gets signed.
    # If anyone modifies the header or payload, the signing input changes -> signature won't match.
    message = header_b64 + b"." + payload_b64

    # =============================================
    # STEP 6: Sign with HMAC-SHA256
    # =============================================
    # HMAC (Hash-based Message Authentication Code):
    #   combines a secret key with the message using SHA-256 hashing
    #   produces a fixed-size (32 byte) signature unique to both the message AND the secret
    #   without the secret, you can't reproduce the same signature -> can't forge the token
    # .digest() returns the raw bytes of the signature
    secret = b"learningapi"  # in production: load from environment variable, NEVER hardcode
    signature = hmac.new(secret, message, hashlib.sha256).digest()

    # =============================================
    # STEP 7: Base64URL Encode the Signature
    # =============================================
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=")

    # =============================================
    # STEP 8: Assemble the Final JWT
    # =============================================
    # Format: base64url(header) . base64url(payload) . base64url(signature)
    # .decode() converts bytes back to a regular Python string for returning/sending
    jwt_token = (message + b"." + signature_b64).decode()

    return jwt_token


# =============================================
# HOW VERIFICATION WORKS (when the server receives a token)
# =============================================
# 1. Split the token by "." -> get header_b64, payload_b64, signature_b64
# 2. Re-create the signing input: header_b64 + "." + payload_b64
# 3. Sign it again with the same secret key using HMAC-SHA256
# 4. Compare the re-computed signature with the received signature_b64
# 5. If they match -> token is valid and untampered
# 6. If they don't match -> token was modified or signed with a different secret -> REJECT
#
# python-jose does all of this in one call:
#   jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#   raises JWTError automatically if the token is invalid, expired, or tampered
