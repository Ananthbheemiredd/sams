# app/routers/fee_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.fee import StudentFee, FeeMaster
from app.models.admissions import Admission
from app.schemas.fee_schema import (
    StudentFeeCreate,
    StudentFeeUpdate,
    StudentFeePayment,
    StudentFeeResponse,
)

router = APIRouter(prefix="/fees", tags=["Fees"])


# ============================================================
# CREATE STUDENT FEE
# ============================================================
@router.post("/", response_model=StudentFeeResponse)
async def create_student_fee(
    payload: StudentFeeCreate,
    db: AsyncSession = Depends(get_session),
):
    # 1️⃣ Validate Admission
    adm_res = await db.execute(
        select(Admission).where(
            Admission.admission_id == payload.admission_id
        )
    )
    admission = adm_res.scalar_one_or_none()
    if not admission:
        raise HTTPException(404, "Admission not found")

    # 2️⃣ Validate Fee Type
    fee_res = await db.execute(
        select(FeeMaster).where(
            FeeMaster.fee_type_id == payload.fee_type_id
        )
    )
    fee_type = fee_res.scalar_one_or_none()
    if not fee_type:
        raise HTTPException(404, "Invalid fee type")

    # 3️⃣ Prevent duplicate fee head for same student
    existing = await db.execute(
        select(StudentFee).where(
            StudentFee.admission_id == payload.admission_id,
            StudentFee.fee_type_id == payload.fee_type_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            400,
            "This fee type already assigned to the student",
        )

    # 4️⃣ Create Fee Record
    net_amount = payload.amount - payload.discount

    student_fee = StudentFee(
        student_fee_id=f"SF-{payload.admission_id}-{payload.fee_type_id}",
        admission_id=payload.admission_id,
        fee_type_id=payload.fee_type_id,
        amount=payload.amount,
        discount=payload.discount,
        discount_reason=payload.discount_reason,
        paid_fee=0,
        pending_fee=net_amount,
        status="unpaid",
    )

    db.add(student_fee)
    await db.commit()
    await db.refresh(student_fee)

    return student_fee


# ============================================================
# GET SINGLE FEE
# ============================================================
@router.get("/{student_fee_id}", response_model=StudentFeeResponse)
async def get_student_fee(
    student_fee_id: str,
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(
        select(StudentFee).where(
            StudentFee.student_fee_id == student_fee_id
        )
    )
    fee = res.scalar_one_or_none()

    if not fee:
        raise HTTPException(404, "Fee not found")

    return fee


# ============================================================
# LIST FEES (FILTERABLE)
# ============================================================
@router.get("/", response_model=list[StudentFeeResponse])
async def list_student_fees(
    admission_id: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(StudentFee)

    if admission_id:
        stmt = stmt.where(StudentFee.admission_id == admission_id)

    if status:
        stmt = stmt.where(StudentFee.status == status)

    res = await db.execute(stmt)
    return res.scalars().all()


# ============================================================
# UPDATE FEE (amount/discount/status)
# ============================================================
@router.patch("/{student_fee_id}", response_model=StudentFeeResponse)
async def update_student_fee(
    student_fee_id: str,
    payload: StudentFeeUpdate,
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(
        select(StudentFee).where(
            StudentFee.student_fee_id == student_fee_id
        )
    )
    fee = res.scalar_one_or_none()

    if not fee:
        raise HTTPException(404, "Fee not found")

    update_data = payload.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(fee, field, value)

    # Recalculate pending if amount/discount changed
    fee.pending_fee = max(
        (fee.amount - fee.discount) - fee.paid_fee,
        0,
    )

    await db.commit()
    await db.refresh(fee)
    return fee


# ============================================================
# PAY FEE
# ============================================================
@router.post("/{student_fee_id}/pay", response_model=StudentFeeResponse)
async def pay_student_fee(
    student_fee_id: str,
    payload: StudentFeePayment,
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(
        select(StudentFee).where(
            StudentFee.student_fee_id == student_fee_id
        )
    )
    fee = res.scalar_one_or_none()

    if not fee:
        raise HTTPException(404, "Fee not found")

    if payload.amount <= 0:
        raise HTTPException(400, "Payment amount must be positive")

    fee.paid_fee += payload.amount
    fee.pending_fee = max(
        (fee.amount - fee.discount) - fee.paid_fee,
        0,
    )

    # Update status
    if fee.pending_fee == 0:
        fee.status = "paid"
    else:
        fee.status = "partial"

    await db.commit()
    await db.refresh(fee)
    return fee
