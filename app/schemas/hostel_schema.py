from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ======================================================
# HOSTEL
# ======================================================

class HostelBase(BaseModel):
    school_id: str
    branch_id: str
    hostel_name: str
    gender_type: Optional[str] = None
    warden_name: Optional[str] = None


class HostelCreate(HostelBase):
    pass


class HostelUpdate(BaseModel):
    hostel_name: Optional[str] = None
    gender_type: Optional[str] = None
    warden_name: Optional[str] = None


class HostelResponse(HostelBase):
    hostel_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ======================================================
# ROOM
# ======================================================

class HostelRoomBase(BaseModel):
    hostel_id: str
    floor_number: int
    room_number: str
    total_beds: int


class HostelRoomCreate(HostelRoomBase):
    pass


class HostelRoomUpdate(BaseModel):
    floor_number: Optional[int] = None
    room_number: Optional[str] = None
    total_beds: Optional[int] = None


class HostelRoomResponse(HostelRoomBase):
    room_id: str

    class Config:
        from_attributes = True


# ======================================================
# ALLOCATION
# ======================================================

class HostelAllocationBase(BaseModel):
    admission_id: str
    room_id: str
    bed_no: int


class HostelAllocationCreate(HostelAllocationBase):
    pass


class HostelAllocationVacate(BaseModel):
    vacate: bool = True


class HostelAllocationResponse(HostelAllocationBase):
    allocation_id: str
    allocated_on: datetime
    vacated_on: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True
