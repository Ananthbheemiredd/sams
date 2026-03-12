import copy
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from app.database.base import get_session
from app.models.payroll_management import (
    Salary_components,
    TaxSlab1,
    SalaryPolicy1,
)
from app.schemas.payroll_management_schema import (
    salryenter,
    SalaryInput,
    SalaryPolicyCreateSchema,
    SalaryPolicyResponseSchema,
    SalaryPolicyUpdateSchema,
    PolicyComponentPatchSchema,
    TaxSlabCreateSchema,
    TaxSlabUpdateSchema,
    TaxSlabResponseSchema,
)
from app.utils.payroll_management_utils import compute_salary_components

router = APIRouter(tags=["Payroll-management"])

@router.post("/salary_breakup/add")
async def add_salary_breakup(
    payload: salryenter,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(SalaryBreakup).where(SalaryBreakup.emp_id == payload.emp_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Salary breakup already exists")

    components = await compute_salary_components(
        payload.annual_ctc, payload.emp_id, payload.regime, db
    )

    record = SalaryBreakup(
        emp_id=payload.emp_id,
        annual_ctc=payload.annual_ctc,
        regime=payload.regime,
        **components,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/salary_breakups", response_model=List[SalaryInput])
async def list_salary_breakups(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SalaryBreakup))
    return result.scalars().all()


@router.get("/salary_breakup/{emp_id}", response_model=SalaryInput)
async def get_salary_breakup(emp_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(SalaryBreakup).where(SalaryBreakup.emp_id == emp_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(404, "Not found")
    return record


@router.put("/salary_breakup/{emp_id}")
async def update_salary_breakup(
    emp_id: int,
    payload: salryenter,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(SalaryBreakup).where(SalaryBreakup.emp_id == emp_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(404, "Not found")

    components = await compute_salary_components(
        payload.annual_ctc, emp_id, payload.regime, db
    )

    record.annual_ctc = payload.annual_ctc
    record.regime = payload.regime
    for k, v in components.items():
        setattr(record, k, v)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/salary_breakup/{emp_id}")
async def delete_salary_breakup(emp_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(SalaryBreakup).where(SalaryBreakup.emp_id == emp_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(404, "Not found")

    await db.delete(record)
    await db.commit()
    return {"detail": "Deleted"}
@router.get("/policy", response_model=List[SalaryPolicyResponseSchema])
async def get_policies(policy_id: Optional[int] = Query(None), db: AsyncSession = Depends(get_session)):
    if policy_id:
        result = await db.execute(select(SalaryPolicy1).where(SalaryPolicy1.id == policy_id))
        policy = result.scalar_one_or_none()
        if not policy:
            raise HTTPException(404, "Not found")
        return [policy]

    result = await db.execute(select(SalaryPolicy1))
    return result.scalars().all()
@router.post("/policy", response_model=SalaryPolicyResponseSchema, status_code=201)
async def create_policy(payload: SalaryPolicyCreateSchema, db: AsyncSession = Depends(get_session)):
    policy = SalaryPolicy1(
        salary_sheet_id="TEMP",
        effective_from=payload.effective_from,
        is_active=payload.is_active,
        salary_range=payload.salary_range.dict(),
        components=[c.dict() for c in payload.components],
    )

    db.add(policy)
    await db.flush()
    policy.salary_sheet_id = f"SAL-{policy.effective_from.year}-{str(policy.id).zfill(4)}"
    await db.commit()
    await db.refresh(policy)
    return policy
@router.get("/slabs", response_model=List[TaxSlabResponseSchema])
async def list_slabs(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(TaxSlab1))
    return result.scalars().all()
@router.post("/slabs", response_model=TaxSlabResponseSchema)
async def create_slab(payload: TaxSlabCreateSchema, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(TaxSlab1).order_by(TaxSlab1.id.desc()))
    last = result.scalars().first()

    slab_id = f"SLAB{int(last.slab_id.replace('SLAB', '')) + 1:03d}" if last else "SLAB001"

    slab = TaxSlab1(
        slab_id=slab_id,
        regime=payload.regime,
        slab_ranges=[s.dict() for s in payload.slab_ranges],
        effective_from=payload.effective_from,
        is_active=payload.is_active,
    )

    db.add(slab)
    await db.commit()
    await db.refresh(slab)
    return slab
