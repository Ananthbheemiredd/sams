from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database.base import get_session
from app.models.school import School
from app.schemas.school_schema import (
    SchoolCreate,
    SchoolUpdate,
    SchoolResponse,
)
from app.schemas.common import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(prefix="/schools", tags=["Schools"])


# =====================================================
# CREATE SCHOOL
# =====================================================
@router.post("/", response_model=SchoolResponse, status_code=201)
async def create_school(
    data: SchoolCreate,
    db: AsyncSession = Depends(get_session),
):
    existing = await db.execute(
        select(School).where(School.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "School code already exists")

    school = School(
        school_id=f"SCH{data.code.upper()}",
        school_name=data.school_name,
        code=data.code,
        city=data.city,
        state=data.state,
        address=data.address,
        phone=data.phone,
        email=data.email,
    )

    db.add(school)
    await db.commit()
    await db.refresh(school)
    return school


# =====================================================
# LIST SCHOOLS (Pagination + Search)
# =====================================================
@router.get("/", response_model=PaginatedResponse[SchoolResponse])
async def list_schools(
    search: str | None = Query(None),
    city: str | None = Query(None),
    is_active: bool | None = Query(None),
    order_by: str = Query("created_at"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * limit

    query = select(School)
    count_query = select(func.count()).select_from(School)

    if search:
        condition = or_(
            School.name.ilike(f"%{search}%"),
            School.code.ilike(f"%{search}%"),
            School.city.ilike(f"%{search}%"),
        )
        query = query.where(condition)
        count_query = count_query.where(condition)

    if city:
        query = query.where(School.city.ilike(f"%{city}%"))
        count_query = count_query.where(School.city.ilike(f"%{city}%"))

    if is_active is not None:
        query = query.where(School.is_active == is_active)
        count_query = count_query.where(School.is_active == is_active)

    # Safe sorting
    sort_column = getattr(School, order_by, School.created_at)
    query = query.order_by(sort_column.desc())

    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    schools = result.scalars().all()

    return paginate(schools, total, page, limit)


# =====================================================
# GET SCHOOL BY ID
# =====================================================
@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(School).where(School.school_id == school_id)
    )
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(404, "School not found")

    return school


# =====================================================
# UPDATE SCHOOL (PATCH)
# =====================================================
@router.patch("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    data: SchoolUpdate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(School).where(School.school_id == school_id)
    )
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(404, "School not found")

    update_data = data.dict(exclude_unset=True)

    # Duplicate code check on update
    if "code" in update_data:
        dup = await db.execute(
            select(School).where(
                School.school_id != school_id,
                School.code == update_data["code"],
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(400, "School code already exists")

    for field, value in update_data.items():
        setattr(school, field, value)

    await db.commit()
    await db.refresh(school)
    return school


# =====================================================
# SOFT DELETE (DEACTIVATE)
# =====================================================
@router.delete("/{school_id}")
async def delete_school(
    school_id: int,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(School).where(School.school_id == school_id)
    )
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(404, "School not found")

    school.is_active = False
    await db.commit()

    return {"message": "School deactivated successfully"}
