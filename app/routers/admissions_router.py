from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.admissions import Admission
from app.models.application_form import Application
from app.schemas.admissions_schema import (
    AdmissionCreate,
    AdmissionUpdate,
    AdmissionResponse,
)
from app.core.role_deps import require_admission_manager

router = APIRouter(prefix="/admissions", tags=["Admissions"])

@router.post("/", response_model=AdmissionResponse)
async def create_admission(
    payload: AdmissionCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_admission_manager),
):
    #  Check application exists
    app_result = await db.execute(
        select(Application).where(
            Application.application_id == payload.application_id
        )
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(404, "Application not found")

    # Prevent duplicate admission
    existing = await db.execute(
        select(Admission).where(
            Admission.application_id == payload.application_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Admission already created")

    #  Create Admission (auto map from application)
    admission = Admission(
        admission_id=payload.admission_id,
        application_id=application.application_id,
        school_id=application.school_id,
        branch_id=application.branch_id,
        student_name=application.full_name,
        student_surname=application.surname,
        class_id=payload.class_id,
        section_id=payload.section_id,
        exam_result=payload.exam_result,
        paid_amount=payload.paid_amount,
        status="ACTIVE",
    )

    db.add(admission)
    await db.commit()
    await db.refresh(admission)
    return admission

@router.get("/{admission_id}", response_model=AdmissionResponse)
async def get_admission(
    admission_id: str,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Admission).where(
            Admission.admission_id == admission_id
        )
    )
    admission = result.scalar_one_or_none()
    if not admission:
        raise HTTPException(404, "Admission not found")
    return admission

@router.get("/by-application/{application_id}", response_model=AdmissionResponse)
async def get_by_application(
    application_id: str,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Admission).where(
            Admission.application_id == application_id
        )
    )
    admission = result.scalar_one_or_none()
    if not admission:
        raise HTTPException(404, "Admission not found")
    return admission


@router.patch("/{admission_id}", response_model=AdmissionResponse)
async def update_admission(
    admission_id: str,
    payload: AdmissionUpdate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_admission_manager),
):
    result = await db.execute(
        select(Admission).where(
            Admission.admission_id == admission_id
        )
    )
    admission = result.scalar_one_or_none()
    if not admission:
        raise HTTPException(404, "Admission not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(admission, key, value)

    await db.commit()
    await db.refresh(admission)
    return admission

@router.get("/", response_model=list[AdmissionResponse])
async def list_admissions(
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Admission))
    return result.scalars().all()







