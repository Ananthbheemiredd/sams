from datetime import datetime, timedelta, timezone
from typing import Dict
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.models.user_session import UserSession


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def session_expiry(hours: int = 8):
    return utc_now() + timedelta(hours=hours)


async def create_user_session(
    db: AsyncSession,
    user_id: int,
    role_type: str
) -> Dict:
    """
    Create a new user session.
    Enforces SINGLE active session per user.
    """

    # 1. Deactivate existing sessions
    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.is_active.is_(True)
        )
        .values(
            is_active=False,
            logout_time=utc_now()
        )
    )

    # 2. Create new session (NO JWT YET)
    session = UserSession(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        role_type=role_type,
        is_active=True,
        login_time=utc_now(),
        expires_at=session_expiry()
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "role_type": session.role_type,
        "login_time": session.login_time,
        "expires_at": session.expires_at,
        "is_active": session.is_active
    }
