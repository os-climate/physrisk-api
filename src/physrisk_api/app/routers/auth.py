"""Token endpoints: exchange an API key for tokens, or refresh an access token."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from physrisk_api.app.auth import (
    REFRESH_TOKEN_EXPIRE_SECONDS,
    TOKEN_EXPIRE_SECONDS,
    issue_refresh_token,
    issue_token,
    validate_api_key,
    validate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = TOKEN_EXPIRE_SECONDS
    refresh_expires_in: int = REFRESH_TOKEN_EXPIRE_SECONDS


@router.post("/token", response_model=TokenResponse)
def get_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> TokenResponse:
    """Exchange an API key for an access token and a refresh token."""
    scopes = validate_api_key(credentials.credentials)
    return TokenResponse(
        access_token=issue_token(scopes),
        refresh_token=issue_refresh_token(scopes),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> TokenResponse:
    """Exchange a refresh token for a new access token and refresh token."""
    scopes = validate_refresh_token(credentials.credentials)
    return TokenResponse(
        access_token=issue_token(scopes),
        refresh_token=issue_refresh_token(scopes),
    )
