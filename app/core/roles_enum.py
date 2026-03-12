# app/core/roles_enum.py
from enum import Enum

class RoleEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    ACCOUNTANT = "ACCOUNTANT"
    RECEPTION = "RECEPTION"
    HOSTEL_WARDEN = "HOSTEL_WARDEN"
    PRINCIPAL = "PRINCIPAL"
    HOD = "HOD"
    VICE_PRINCIPAL = "VICE_PRINCIPAL"
    HR = "HR"
