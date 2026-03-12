# app/routers/branch_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.base import get_session
from app.models.branch import Branch
from app.models.school import School
from app.schemas.branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
)

router = APIRouter(prefix="/branches", tags=["Branches"])

@router.post("/", response_model=BranchResponse, status_code=201)
async def create_branch(
    data: BranchCreate,
    db: AsyncSession = Depends(get_session),
):
    # FK check
    school = await db.execute(
        select(School).where(School.school_id == data.school_id)
    )
    if not school.scalar_one_or_none():
        raise HTTPException(400, "Invalid school_id")

    # Duplicate code check
    existing = await db.execute(
        select(Branch).where(Branch.branch_code == data.branch_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Branch code already exists")

    branch_id = f"BR{data.branch_code.upper()}"

    branch = Branch(
        branch_id=branch_id,
        **data.dict()
    )

    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.get("/", response_model=list[BranchResponse])
async def get_all_branches(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Branch))
    return result.scalars().all()

@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(branch_id: str, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Branch).where(Branch.branch_id == branch_id)
    )
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(404, "Branch not found")

    return branch

@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: str,
    data: BranchUpdate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Branch).where(Branch.branch_id == branch_id)
    )
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(404, "Branch not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(branch, key, value)

    await db.commit()
    await db.refresh(branch)
    return branch

@router.delete("/{branch_id}")
async def delete_branch(branch_id: str, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Branch).where(Branch.branch_id == branch_id)
    )
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(404, "Branch not found")

    branch.is_active = False
    await db.commit()

    return {"message": "Branch deactivated successfully"}
