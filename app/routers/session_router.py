from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.base import get_session
from app.models.user_session import UserSession
from app.schemas.session_schema import UserSessionResponse
from app.core.auth_dependencies import require_access_token

router = APIRouter(prefix="/sessions", tags=["User Sessions"])


# =========================================================
# 1. LIST MY SESSIONS (Logged-in user only)
# =========================================================
@router.get("/me", response_model=list[UserSessionResponse])
async def get_my_sessions(
    user: dict = Depends(require_access_token),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == int(user["sub"]))
        .order_by(
            desc(UserSession.is_active),
            desc(UserSession.login_time),
        )
    )
    return result.scalars().all()


# =========================================================
# 2. GET A SPECIFIC SESSION (Only own session)
# =========================================================
@router.get("/{session_id}", response_model=UserSessionResponse)
async def get_session_by_id(
    session_id: str,
    user: dict = Depends(require_access_token),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserSession).where(
            UserSession.session_id == session_id,
            UserSession.user_id == int(user["sub"]),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(404, "Session not found")

    return session


# =========================================================
# 3. LOGOUT / DEACTIVATE A SESSION (Own session)
# =========================================================
@router.post("/{session_id}/deactivate")
async def deactivate_session(
    session_id: str,
    user: dict = Depends(require_access_token),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserSession).where(
            UserSession.session_id == session_id,
            UserSession.user_id == int(user["sub"]),
            UserSession.is_active.is_(True),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(404, "Active session not found")

    session.is_active = False
    await db.commit()

    return {"message": "Session deactivated successfully"}


# =========================================================
# 4. DELETE SESSION RECORD (Own session history)
# =========================================================
@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    user: dict = Depends(require_access_token),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserSession).where(
            UserSession.session_id == session_id,
            UserSession.user_id == int(user["sub"]),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(404, "Session not found")

    await db.delete(session)
    await db.commit()

    return {"message": "Session deleted successfully"}
