# app/schemas/branch_schema.py
from pydantic import BaseModel, EmailStr


class BranchCreate(BaseModel):
    branch_name: str
    branch_code: str
    school_id: str
    city: str
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class BranchUpdate(BaseModel):
    branch_name: str | None = None
    city: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class BranchResponse(BaseModel):
    branch_id: str
    branch_name: str
    branch_code: str
    school_id: str
    city: str
    address: str | None
    phone: str | None
    email: str | None
    is_active: bool

    class Config:
        from_attributes = True
