"""JWT issuance and validation for the Physrisk API."""

import json
import os
import time
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 3600
REFRESH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days

_bearer = HTTPBearer(auto_error=False)


def _jwt_secret() -> str:
    secret = os.environ.get("PHYSRISK_JWT_SECRET")
    if not secret:
        raise RuntimeError("PHYSRISK_JWT_SECRET env var not set")
    return secret


def _api_keys() -> dict[str, list[str]]:
    # Maps API key → list of scopes, e.g. {"my-key": ["jba/api"]}
    return json.loads(os.environ.get("PHYSRISK_API_KEYS", "{}"))


def validate_api_key(key: str) -> list[str]:
    """Validate an API key and return its scopes. Replace with OIDC validation later."""
    scopes = _api_keys().get(key)
    if scopes is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return scopes


def issue_token(scopes: list[str]) -> str:
    """Issue a signed access JWT embedding the given scopes."""
    now = int(time.time())
    payload = {
        "type": "access",
        "scopes": scopes,
        "iat": now,
        "exp": now + TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=ALGORITHM)


def issue_refresh_token(scopes: list[str]) -> str:
    """Issue a signed refresh JWT embedding the given scopes."""
    now = int(time.time())
    payload = {
        "type": "refresh",
        "scopes": scopes,
        "iat": now,
        "exp": now + REFRESH_TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=ALGORITHM)


def validate_refresh_token(token: str) -> list[str]:
    """Validate a refresh token and return its scopes."""
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    return payload.get("scopes", [])


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    """FastAPI dependency: accept a physrisk JWT or a raw API key; return empty scopes if absent."""
    if credentials is None:
        return {"scopes": []}
    token = credentials.credentials
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[ALGORITHM])
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Use access token, not refresh token",
            )
        return payload
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.PyJWTError:
        pass  # not a JWT — try as an API key
    scopes = _api_keys().get(token)
    if scopes is not None:
        return {"scopes": scopes}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    )


JBA_MAX_REQUESTS = 20


def provider_limits(user: dict) -> dict[str, int]:
    """Return provider_max_requests dict based on user scopes."""
    return {"jba": JBA_MAX_REQUESTS if "jba/api" in user.get("scopes", []) else -1}


def require_scope(scope: str):
    """FastAPI dependency factory that enforces a named scope on a route."""

    def check(user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if scope not in user.get("scopes", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{scope}' required",
            )
        return user

    return check
