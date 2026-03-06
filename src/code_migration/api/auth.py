import secrets
from fastapi import Security, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from code_migration.config import settings

X_API_KEY = APIKeyHeader(name="X-API-Key", auto_error=False)

# Optional: Add multiple valid keys or read from DB here.
# For now, we mock it via a single env var or allow open access if no key is configured
# in the environment, assuming developer use locally.
# In a real enterprise version, this would validate against an auth service.

def verify_api_key(api_key: str = Security(X_API_KEY)):
    """
    Verify API key if one is configured in the environment.
    If MIGRATION_API_KEY is defined but missing in request, return 401.
    """
    import os
    expected_key = os.environ.get("MIGRATION_API_KEY")

    if not expected_key:
        return True  # Auth Disabled natively

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return True
