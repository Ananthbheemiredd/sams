# # =====================================================================================
# # PAYROLL MANAGEMENT UTILS – SAMS
# # =====================================================================================
#
# import os
# import json
# import calendar
# import logging
# from datetime import datetime, date, timedelta
# from pathlib import Path
# from io import BytesIO
# from typing import Dict, List, Optional
#
# import PyPDF2
# from sqlalchemy.orm import Session
# from sqlalchemy import func
#
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Paragraph, Frame
# from reportlab.lib import colors
# from reportlab.lib.units import mm
# from reportlab.lib.utils import ImageReader
#
# # =====================================================================================
# # MODELS (FIXED PATHS)
# # =====================================================================================
#
# from app.models.profile_information import ProfileInformation
# from app.models.payroll_management import (
#     PayrollCycle,
#     SalaryExcelSheet,
#     Payslip,
#     PayslipAction,
#     SalaryComponentName,
#     Salary_components,
#     SalaryPolicy1,
#     TaxSlab1,
#     Bonus,
#     BonusType,
#     Arrear,
#     ArrearType,
#     Expenseclaim,
#     ExpenseType,
# )
#
# # =====================================================================================
# # LOGGER
# # =====================================================================================
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # =====================================================================================
# # BASIC FETCH HELPERS
# # =====================================================================================
#
# def get_employee_profile(employee_id: str, db: Session):
#     profile = (
#         db.query(ProfileInformation)
#         .filter(ProfileInformation.employee_id == employee_id)
#         .first()
#     )
#     if not profile:
#         raise ValueError(f"No profile found for employee ID: {employee_id}")
#     return profile
#
#
# def get_designation(designation_id: str, db: Session):
#     if not designation_id:
#         return ""
#     d = (
#         db.query(Designation)
#         .filter(Designation.designation_id == designation_id)
#         .first()
#     )
#     return d.designation_name if d else ""
#
#
# def get_band(band_id: str, db: Session):
#     if not band_id:
#         return ""
#     b = db.query(UserBand).filter(UserBand.band_id == band_id).first()
#     return b.band_name if b else ""
#
#
# def get_full_name(profile: ProfileInformation) -> str:
#     return f"{profile.first_name or ''} {profile.last_name or ''}".strip().title()
#
# # =====================================================================================
# # TIMESHEET SUMMARY (UNCHANGED LOGIC)
# # =====================================================================================
#
# def fetch_timesheet_summary(
#     emp_id: str,
#     year: int,
#     month: int,
#     db: Session,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
# ):
#     if not start_date:
#         start_date = date(year, month, 1)
#     if not end_date:
#         end_date = date(year, month, calendar.monthrange(year, month)[1])
#
#     profile = get_employee_profile(emp_id, db)
#     doj = profile.hire_date
#     eligible_start_date = max(start_date, doj) if doj else start_date
#
#     # ---- Weekly Offs ----
#     weekly_offs = []
#     shift = (
#         db.query(ShiftAssignment)
#         .filter(
#             ShiftAssignment.employee_id == emp_id,
#             ShiftAssignment.effective_from <= end_date,
#             (ShiftAssignment.effective_to.is_(None))
#             | (ShiftAssignment.effective_to >= start_date),
#         )
#         .first()
#     )
#
#     if shift and shift.weekly_off:
#         rules = shift.weekly_off.weekly_offs.get("rules", [])
#         curr = start_date
#         while curr <= end_date:
#             week_no = ((curr.day - 1) // 7) + 1
#             for r in rules:
#                 if r.get("day") == curr.strftime("%A"):
#                     if not r.get("weeks") or week_no in r.get("weeks"):
#                         weekly_offs.append(curr)
#             curr += timedelta(days=1)
#
#     # ---- Holidays ----
#     holidays = set()
#     if profile.holiday_template_id:
#         holidays = {
#             h.holiday_date
#             for h in db.query(HolidayCalendar)
#             .join(HolidayAssignment)
#             .filter(
#                 HolidayAssignment.template_id == profile.holiday_template_id,
#                 HolidayCalendar.holiday_date.between(start_date, end_date),
#             )
#         }
#
#     # ---- Leaves ----
#     leave_requests = (
#         db.query(LeaveRequest)
#         .join(LeaveCategory)
#         .filter(
#             LeaveRequest.employee_id == emp_id,
#             LeaveRequest.status == "Approved",
#             LeaveRequest.end_date >= eligible_start_date,
#             LeaveRequest.start_date <= end_date,
#         )
#         .all()
#     )
#
#     leave_map = {}
#     for lr in leave_requests:
#         for i in range((lr.end_date - lr.start_date).days + 1):
#             d = lr.start_date + timedelta(days=i)
#             if eligible_start_date <= d <= end_date:
#                 leave_map[d] = lr.category.is_paid
#
#     # ---- Timesheet ----
#     ts_entries = (
#         db.query(Timesheet)
#         .filter(
#             Timesheet.employee_id == emp_id,
#             Timesheet.week_start_date <= end_date,
#             Timesheet.week_end_date >= eligible_start_date,
#             Timesheet.status == "Approved",
#         )
#         .all()
#     )
#
#     day_map: Dict[date, float] = {}
#     for ts in ts_entries:
#         for k, v in (ts.working_hours or {}).items():
#             d = date.fromisoformat(k)
#             day_map[d] = day_map.get(d, 0) + float(v.get("work_hours", 0))
#
#     # ---- Final Counts ----
#     total_working_days = 0
#     lop_days = 0
#     present_days = 0
#
#     curr = eligible_start_date
#     while curr <= end_date:
#         if curr not in holidays and curr not in weekly_offs:
#             total_working_days += 1
#             hrs = day_map.get(curr, 0)
#             if hrs >= 8:
#                 present_days += 1
#             else:
#                 lop_days += 1
#         curr += timedelta(days=1)
#
#     return {
#         "total_month_days": (end_date - start_date).days + 1,
#         "eligible_days": (end_date - eligible_start_date).days + 1,
#         "total_working_days": total_working_days,
#         "present_days": present_days,
#         "lop_days": lop_days,
#         "days_worked": present_days,
#         "paid_leaves": 0,
#         "overtime_hours": 0,
#     }
#
# # =====================================================================================
# # TAX CALCULATION
# # =====================================================================================
#
# def calculate_annual_tax_flat(annual_ctc: float, slab_ranges: List[Dict]) -> float:
#     for slab in slab_ranges:
#         if slab["lower_limit"] <= annual_ctc <= slab["upper_limit"]:
#             return round(annual_ctc * slab["rate"], 2)
#     return 0.0
#
# # =====================================================================================
# # CONFIG LOADER
# # =====================================================================================
#
# def load_config():
#     config_path = Path(__file__).resolve().parent.parent / "config" / "payslip_settings.json"
#     if not config_path.exists():
#         raise FileNotFoundError(f"Missing config: {config_path}")
#     with config_path.open("r", encoding="utf-8") as f:
#         return json.load(f)
#
# # =====================================================================================
# # PASSWORD
# # =====================================================================================
#
# def generate_password(emp_data: Dict, default="1234"):
#     doj = emp_data.get("doj", "")
#     emp_id = emp_data.get("emp_id", "")
#     digits = "".join(filter(str.isdigit, doj))[-4:]
#     return f"{emp_id}{digits}" if digits else default
