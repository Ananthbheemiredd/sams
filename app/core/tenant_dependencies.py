from fastapi import Depends, HTTPException
from app.core.auth_dependencies import require_access_token


def get_tenant_context(payload=Depends(require_access_token)):
    return {
        "user_id": payload["sub"],
        "role": payload["role"],
        "school_id": payload.get("school_id"),
        "branch_id": payload.get("branch_id"),
    }


def require_school_context(ctx=Depends(get_tenant_context)):
    if not ctx["school_id"]:
        raise HTTPException(403, "School context required")
    return ctx
