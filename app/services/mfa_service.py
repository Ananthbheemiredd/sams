import pyotp
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.mfa_secret import MFASecret


async def get_or_create_mfa(
    db: AsyncSession,
    user_id: int,
    role_type: str
) -> MFASecret:
    """
    Get MFA record or allow re-enrollment if disabled
    """

    result = await db.execute(
        select(MFASecret).where(
            MFASecret.user_id == user_id,
            MFASecret.role_type == role_type
        )
    )
    mfa = result.scalar_one_or_none()

    #  First-time enrollment
    if not mfa:
        mfa = MFASecret(
            user_id=user_id,
            role_type=role_type,
            secret_key=pyotp.random_base32(),
            is_enabled=False,
            backup_codes=[]
        )
        db.add(mfa)
        await db.commit()
        await db.refresh(mfa)
        return mfa

    #  Already enabled → block
    if mfa.is_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA already enabled for this account"
        )

    # Re-enrollment allowed (disabled MFA)
    mfa.secret_key = pyotp.random_base32()
    mfa.backup_codes = []
    await db.commit()
    await db.refresh(mfa)

    return mfa







