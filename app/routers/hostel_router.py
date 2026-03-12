from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.base import get_session
from app.models.hostel import Hostel, HostelRoom, HostelAllocation
from app.models.admissions import Admission
from app.schemas.hostel_schema import (
    HostelCreate, HostelUpdate, HostelResponse,
    HostelRoomCreate, HostelRoomUpdate, HostelRoomResponse,
    HostelAllocationCreate, HostelAllocationResponse
)

router = APIRouter(prefix="/hostels", tags=["Hostels"])

@router.post("/", response_model=HostelResponse)
async def create_hostel(payload: HostelCreate, db: AsyncSession = Depends(get_session)):
    hostel = Hostel(**payload.dict())
    db.add(hostel)
    await db.commit()
    await db.refresh(hostel)
    return hostel

@router.post("/allocations", response_model=HostelAllocationResponse)
async def allocate_bed(payload: HostelAllocationCreate, db: AsyncSession = Depends(get_session)):
    # Validate admission
    admission = await db.get(Admission, payload.admission_id)
    if not admission:
        raise HTTPException(404, "Admission not found")

    # Validate room
    room = await db.get(HostelRoom, payload.room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    # Count active allocations in this room
    count_res = await db.execute(
        select(func.count(HostelAllocation.allocation_id)).where(
            HostelAllocation.room_id == payload.room_id,
            HostelAllocation.status == "ACTIVE"
        )
    )
    occupied = count_res.scalar()

    if occupied >= room.total_beds:
        raise HTTPException(400, "Room is full")

    # Check bed already taken
    bed_check = await db.execute(
        select(HostelAllocation).where(
            HostelAllocation.room_id == payload.room_id,
            HostelAllocation.bed_no == payload.bed_no,
            HostelAllocation.status == "ACTIVE"
        )
    )
    if bed_check.scalar_one_or_none():
        raise HTTPException(400, "Bed already allocated")

    allocation = HostelAllocation(
        allocation_id=f"ALL{payload.admission_id}{payload.room_id}",
        admission_id=payload.admission_id,
        room_id=payload.room_id,
        bed_no=payload.bed_no,
        allocated_on=datetime.utcnow(),
        status="ACTIVE",
    )

    db.add(allocation)
    await db.commit()
    await db.refresh(allocation)
    return allocation

@router.post("/allocations/{allocation_id}/vacate", response_model=HostelAllocationResponse)
async def vacate_bed(allocation_id: str, db: AsyncSession = Depends(get_session)):
    allocation = await db.get(HostelAllocation, allocation_id)
    if not allocation or allocation.status != "ACTIVE":
        raise HTTPException(404, "Active allocation not found")

    allocation.status = "VACATED"
    allocation.vacated_on = datetime.utcnow()

    await db.commit()
    await db.refresh(allocation)
    return allocation

@router.get("/{hostel_id}/rooms")
async def list_rooms(hostel_id: str, db: AsyncSession = Depends(get_session)):
    rooms = (await db.execute(
        select(HostelRoom).where(HostelRoom.hostel_id == hostel_id)
    )).scalars().all()

    response = []
    for room in rooms:
        count = (await db.execute(
            select(func.count(HostelAllocation.allocation_id)).where(
                HostelAllocation.room_id == room.room_id,
                HostelAllocation.status == "ACTIVE"
            )
        )).scalar()

        response.append({
            "room_id": room.room_id,
            "total_beds": room.total_beds,
            "occupied": count,
            "available": room.total_beds - count
        })

    return response

@router.get("/allocations", response_model=list[HostelAllocationResponse])
async def list_allocations(
    room_id: str | None = None,
    admission_id: str | None = None,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(HostelAllocation)

    if room_id:
        stmt = stmt.where(HostelAllocation.room_id == room_id)
    if admission_id:
        stmt = stmt.where(HostelAllocation.admission_id == admission_id)

    res = await db.execute(stmt)
    return res.scalars().all()
