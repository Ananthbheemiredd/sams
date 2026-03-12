# import enum
# from datetime import datetime
# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     Float,
#     DateTime,
#     Enum,
#     ForeignKey,
#     LargeBinary,
#     Boolean, Date
# )
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
#
# from app.database.base import Base
#
#
# # ======================================================
# # ENUMS
# # ======================================================
#
# class ArrearType(enum.Enum):
#     SALARY_REVISION = "salary_revision"
#     APPRAISAL = "appraisal"
#
#
# class BonusType(enum.Enum):
#     FESTIVAL = "festival"
#     REFERRAL = "referral"
#     OTHER = "other"
#
#
# class ExpenseType(enum.Enum):
#     TRAVEL = "travel"
#     FOOD = "food"
#     WIFI = "wifi"
#     HEALTH = "health"
#
#
# # ======================================================
# # SALARY COMPONENT
# # ======================================================
#
# class SalaryComponent(Base):
#     __tablename__ = "salary_components_old"
#
#     id = Column(Integer, primary_key=True)
#
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
#     emp_id = Column(String(100), nullable=False)
#
#     month = Column(Integer, nullable=False)
#     year = Column(Integer, nullable=False)
#
#     annual_ctc = Column(Float, nullable=False)
#     monthly_ctc = Column(Float, nullable=False)
#
#     basic_salary = Column(Float)
#     hra = Column(Float)
#     food_allowance = Column(Float)
#     special_allowance = Column(Float)
#     other_allowance = Column(Float)
#
#     pf_employee = Column(Float)
#     pf_employer = Column(Float)
#     professional_tax = Column(Float)
#
#     lop_days = Column(Integer, default=0)
#     lop_amount = Column(Float, default=0)
#
#     total_ctc = Column(Float)
#     net_salary = Column(Float)
#
#     regime = Column(String(20))
#
#     created_at = Column(DateTime, server_default=func.now())
#
#     user = relationship("User", back_populates="salary_components")
#
#
# # ======================================================
# # ARREARS
# # ======================================================
#
# class Arrear(Base):
#     __tablename__ = "arrears"
#
#     id = Column(Integer, primary_key=True)
#     employee_id = Column(String(100))
#     month = Column(Integer)
#     year = Column(Integer)
#     amount = Column(Float)
#     type = Column(Enum(ArrearType))
#     reason = Column(String(255))
#
#
# # ======================================================
# # BONUS
# # ======================================================
#
# class Bonus(Base):
#     __tablename__ = "bonuses"
#
#     id = Column(Integer, primary_key=True)
#     employee_id = Column(String(100))
#     month = Column(Integer)
#     year = Column(Integer)
#     amount = Column(Float)
#     type = Column(Enum(BonusType))
#     remarks = Column(String(255))
#
#
# # ======================================================
# # EXPENSES
# # ======================================================
#
# class ExpenseClaim(Base):
#     __tablename__ = "expense_claims"
#
#     id = Column(Integer, primary_key=True)
#     employee_id = Column(String(100))
#     expense_type = Column(Enum(ExpenseType))
#     bill_number = Column(String(100))
#     amount = Column(Float)
#     description = Column(String(255))
#     receipt = Column(LargeBinary)
#
#
# # ======================================================
# # PAYSLIP
# # ======================================================
#
# class Payslip(Base):
#     __tablename__ = "payslips"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(100))
#     year = Column(Integer)
#     month = Column(Integer)
#
#     file_name = Column(String(255))
#     file_data = Column(LargeBinary)
#
#     status = Column(String(50), default="GENERATED")
#     approved_at = Column(DateTime)
#
#
# # ======================================================
# # PAYSLIP ACTION LOG
# # ======================================================
#
# class PayslipAction(Base):
#     __tablename__ = "payslip_actions"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(100))
#     action_by = Column(String(100))
#     action_type = Column(String(50))
#     timestamp = Column(DateTime, server_default=func.now())
#
#
# # ======================================================
# # PAYROLL CYCLE
# # ======================================================
#
# class PayrollCycle(Base):
#     __tablename__ = "payroll_cycles"
#
#     id = Column(Integer, primary_key=True)
#     month = Column(Integer)
#     year = Column(Integer)
#     generated_at = Column(DateTime, default=datetime.utcnow)
#     status = Column(String(50), default="Pending")
#
#
# # ======================================================
# # SALARY EXCEL SHEET
# # ======================================================
#
# class SalaryExcelSheet(Base):
#     __tablename__ = "salary_excel_sheets"
#
#     id = Column(Integer, primary_key=True)
#     organization = Column(String(200))
#     shift = Column(String(200))
#     year = Column(Integer)
#     month = Column(Integer)
#     filename = Column(String(200))
#     filedata = Column(LargeBinary)
#
#
# # ======================================================
# # POLICY
# # ======================================================
#
# class Policy(Base):
#     __tablename__ = "policies"
#
#     id = Column(Integer, primary_key=True)
#     policy_name = Column(String(150), nullable=False)
#     description = Column(String(500))
#     is_active = Column(Boolean, default=True)
#
#
# # ======================================================
# # SLAB
# # ======================================================
#
# class Slab(Base):
#     __tablename__ = "slabs"
#
#     id = Column(Integer, primary_key=True)
#     slab_name = Column(String(100), nullable=False)
#     min_amount = Column(Float, nullable=False)
#     max_amount = Column(Float, nullable=False)
#     percentage = Column(Float, nullable=False)
#     is_active = Column(Boolean, default=True)
#
#
#
#
# class PayrollRun(Base):
#     __tablename__ = "payroll_runs"
#
#     id = Column(Integer, primary_key=True)
#     month = Column(Integer)
#     year = Column(Integer)
#     status = Column(String(20), default="DRAFT")  # DRAFT / LOCKED / PAID
#     created_at = Column(Date, default=datetime.utcnow)
#
#
# class Attendance(Base):
#     __tablename__ = "attendance"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(50))
#     date = Column(Date)
#     status = Column(String(20))  # PRESENT / ABSENT / LEAVE
#
#
# class LeaveRequest(Base):
#     __tablename__ = "leave_requests"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(50))
#     from_date = Column(Date)
#     to_date = Column(Date)
#     reason = Column(String(255))
#     status = Column(String(20), default="PENDING")
#
#
# class TaxDeclaration(Base):
#     __tablename__ = "tax_declarations"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(50))
#     section = Column(String(20))
#     amount = Column(Float)
#
#
# class PayrollApproval(Base):
#     __tablename__ = "payroll_approvals"
#
#     id = Column(Integer, primary_key=True)
#     emp_id = Column(String(50))
#     month = Column(Integer)
#     year = Column(Integer)
#     status = Column(String(20))  # APPROVED / REJECTED
