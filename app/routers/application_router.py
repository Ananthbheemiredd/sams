from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.base import get_session
from app.models.application_form import Application
from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
)
from app.notification.notification_service import notify_user
from app.core.auth_dependencies import require_access_token

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationOut)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_access_token),
):
    new_app = Application(**data.dict())

    db.add(new_app)
    try:
        await db.commit()
        await db.refresh(new_app)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Application ID already exists")

    #  Notification (email + in-app safe)
    try:
        await notify_user(
            db=db,
            user_id=user.user_id,
            role=user.role,
            module="APPLICATION",
            title="Application Submitted",
            message=f"Application {new_app.application_id} submitted successfully",
            data={"application_id": new_app.application_id},
            email=new_app.email,
        )
    except Exception as e:
        print("Notification error:", e)

    return new_app

@router.get("/", response_model=list[ApplicationOut])
async def list_applications(
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Application))
    return result.scalars().all()

@router.get("/{application_id}", response_model=ApplicationOut)
async def get_application(
    application_id: str,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Application).where(
            Application.application_id == application_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(404, "Application not found")

    return entry

@router.put("/{application_id}", response_model=ApplicationOut)
async def update_application(
    application_id: str,
    update_data: ApplicationUpdate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_access_token),
):
    result = await db.execute(
        select(Application).where(
            Application.application_id == application_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(404, "Application not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)

    #  Notification on update
    try:
        await notify_user(
            db=db,
            user_id=user.user_id,
            role=user.role,
            module="APPLICATION",
            title="Application Updated",
            message=f"Application {application_id} updated",
            data={"application_id": application_id},
        )
    except Exception as e:
        print("Notification error:", e)

    return entry

@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_access_token),
):
    result = await db.execute(
        select(Application).where(
            Application.application_id == application_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(404, "Application not found")

    await db.delete(entry)
    await db.commit()

    return {"message": "Application deleted successfully"}








