from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.pre_registration import PreRegistration
from app.schemas.pre_registration_schema import (
    PreRegistrationCreate,
    PreRegistrationResponse,
)

from app.services.email import send_email  # <-- your email util

router = APIRouter(prefix="/pre-registration", tags=["Pre Registration"])


# ============================================================
# CREATE
# ============================================================
@router.post("/", response_model=PreRegistrationResponse)

async def create_pre_registration(
    data: PreRegistrationCreate,
    db: AsyncSession = Depends(get_session),
):
    entry = PreRegistration(
        school_id=data.school_id,
        branch_id=data.branch_id,
        class_id=data.class_id,  #  matches table

        student_full_name=data.student_full_name,
        age=data.age,
        gender=data.gender,

        parent_or_guardian_name=data.parent_or_guardian_name,
        relationship=data.relationship,
        phone_no=data.phone_no,
        email=data.email,

        address=data.address,
        state=data.state,
        city=data.city,

        previous_school=data.previous_school,
        remarks=data.remarks,
    )

    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

# ============================================================
# LIST
# ============================================================
@router.get("/", response_model=list[PreRegistrationResponse])
async def list_pre_registrations(
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(PreRegistration))
    return result.scalars().all()


# ============================================================
# GET BY ID
# ============================================================
@router.get("/{pre_registration_id}", response_model=PreRegistrationResponse)
async def get_pre_registration(
    pre_registration_id: str,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(PreRegistration).where(
            PreRegistration.pre_registration_id == pre_registration_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pre-registration not found",
        )

    return entry


# ============================================================
# UPDATE
# ============================================================
@router.patch("/{pre_registration_id}", response_model=PreRegistrationResponse)
async def update_pre_registration(
    pre_registration_id: str,
    update_data: PreRegistrationCreate,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(PreRegistration).where(
            PreRegistration.pre_registration_id == pre_registration_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pre-registration not found",
        )

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)

    # -------- Email ----------
    if entry.email:
        try:
            send_email(
                to_email=entry.email,
                subject="Pre-Registration Updated",
                text=(
                    f"Dear {entry.student_full_name},\n\n"
                    "Your pre-registration details were updated.\n\n"
                    "If you did not request this, please contact support.\n\n"
                    "Regards,\nSAMS Team"
                )
            )
        except Exception as e:
            print("Email error:", e)

    return entry


# ============================================================
# DELETE
# ============================================================
@router.delete("/{pre_registration_id}")
async def delete_pre_registration(
    pre_registration_id: str,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(PreRegistration).where(
            PreRegistration.pre_registration_id == pre_registration_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pre-registration not found",
        )

    email = entry.email
    name = entry.student_full_name

    await db.delete(entry)
    await db.commit()

    # -------- Email ----------
    if email:
        try:
            send_email(
                to_email=email,
                subject="Pre-Registration Removed",
                text=(
                    f"Dear {name},\n\n"
                    "Your pre-registration record has been removed.\n\n"
                    "Regards,\nSAMS Team"
                )
            )
        except Exception as e:
            print("Email error:", e)

    return {"message": "Deleted successfully"}




