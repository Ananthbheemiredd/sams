# app/routers/profile_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.base import get_session
from app.models.profile_information import ProfileInformation
from app.schemas.profile_schema import (
    ProfileInformationCreate,
    ProfileInformationResponse,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/", response_model=ProfileInformationResponse, status_code=201)
async def create_profile(
    payload: ProfileInformationCreate,
    db: AsyncSession = Depends(get_session),
):
    # Duplicate check
    duplicate = await db.execute(
        select(ProfileInformation).where(
            (ProfileInformation.employee_code == payload.employee_code)
            | (ProfileInformation.pan_number == payload.pan_number)
            | (ProfileInformation.aadhaar_number == payload.aadhaar_number)
        )
    )
    if duplicate.scalar_one_or_none():
        raise HTTPException(400, "Employee/PAN/Aadhaar already exists")

    # Convert manager_code -> manager_id
    manager_id_int = None
    if payload.manager_code:
        manager_row = await db.execute(
            select(ProfileInformation.employee_id).where(
                ProfileInformation.employee_code == payload.manager_code
            )
        )
        manager_id_int = manager_row.scalar_one_or_none()
        if not manager_id_int:
            raise HTTPException(400, "Invalid manager employee code")

    profile = ProfileInformation(
        employee_code=payload.employee_code,
        manager_id=manager_id_int,
        user_id=payload.user_id,
        school_id=payload.school_id,
        branch_id=payload.branch_id,

        first_name=payload.first_name,
        last_name=payload.last_name,
        gender=payload.gender,
        date_of_birth=payload.date_of_birth,
        blood_group=payload.blood_group,
        marital_status=payload.marital_status,

        email=payload.email,
        contact_number=payload.contact_number,
        emergency_contact_number=payload.emergency_contact_number,
        current_address=payload.current_address,
        permanent_address=payload.permanent_address,

        designation=payload.designation,
        department=payload.department,
        staff_type=payload.staff_type,
        hire_date=payload.hire_date,
        is_faculty=payload.is_faculty,

        uan=payload.uan,
        pan_number=payload.pan_number,
        aadhaar_number=payload.aadhaar_number,
        pf_number=payload.pf_number,
        esi_number=payload.esi_number,

        annual_ctc=payload.annual_ctc,
        bank_name=payload.bank_name,
        ifsc_code=payload.ifsc_code,
        account_number=payload.account_number,
        name_of_account_holder=payload.name_of_account_holder,

        total_experience=payload.total_experience,
        employee_experience=payload.employee_experience,
        employee_education=payload.employee_education,
        skills=payload.skills,
        is_active=payload.is_active,
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/", response_model=list[ProfileInformationResponse])
async def get_profiles(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ProfileInformation))
    return result.scalars().all()

@router.get("/{employee_id}", response_model=ProfileInformationResponse)
async def get_profile(employee_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(ProfileInformation).where(
            ProfileInformation.employee_id == employee_id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

@router.put("/{employee_id}", response_model=ProfileInformationResponse)
async def update_profile(
    employee_id: int,
    payload: ProfileInformationCreate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(ProfileInformation).where(
            ProfileInformation.employee_id == employee_id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found")

    for key, value in payload.dict().items():
        if key == "manager_code":
            continue
        setattr(profile, key, value)

    if payload.manager_code:
        manager_row = await db.execute(
            select(ProfileInformation.employee_id).where(
                ProfileInformation.employee_code == payload.manager_code
            )
        )
        profile.manager_id = manager_row.scalar_one()

    await db.commit()
    await db.refresh(profile)
    return profile

@router.delete("/{employee_id}")
async def delete_profile(employee_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(ProfileInformation).where(
            ProfileInformation.employee_id == employee_id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found")

    await db.delete(profile)
    await db.commit()
    return {"message": "Profile deleted"}






