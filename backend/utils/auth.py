"""
Authentication Utilities for MedAI-Pro with Clerk
FastAPI dependencies for Clerk token verification
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import jwt
from jwt import PyJWKClient


# Clerk configuration
CLERK_FRONTEND_API = os.getenv('CLERK_FRONTEND_API', '')
CLERK_JWKS_URL = f"https://{CLERK_FRONTEND_API}/.well-known/jwks.json"

# Security scheme
security = HTTPBearer()


def verify_clerk_token(token: str) -> Optional[str]:
    """
    Verify Clerk JWT token
    Returns user_id if valid, None otherwise
    """
    try:
        # Get JWKS client
        jwks_client = PyJWKClient(CLERK_JWKS_URL)

        # Get signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )

        # Return user ID from token
        return payload.get('sub')

    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


async def require_clerk_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to require Clerk authentication
    Returns user_id from verified token
    Raises HTTPException if token is invalid
    """
    token = credentials.credentials
    user_id = verify_clerk_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def optional_clerk_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    FastAPI dependency for optional Clerk authentication
    Returns user_id if token is valid, None otherwise
    Does not raise exception if token is missing or invalid
    """
    if not credentials:
        return None

    token = credentials.credentials
    user_id = verify_clerk_token(token)

    return user_id

