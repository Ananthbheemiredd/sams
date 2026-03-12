# # =====================================================================================
# # STANDARD LIBRARIES
# # =====================================================================================
#
# import copy
# import io
# import os
# import re
# import calendar
# import logging
# from time import time
# from enum import Enum
# from datetime import date, datetime
# from typing import Optional, Dict, List, Tuple, Annotated
# from io import BytesIO
#
# # =====================================================================================
# # FASTAPI
# # =====================================================================================
#
# from fastapi import (
#     APIRouter,
#     BackgroundTasks,
#     Depends,
#     HTTPException,
#     Query,
#     UploadFile,
#     File,
#     Form,
#     Body,
#     status,
# )
# from fastapi.responses import StreamingResponse, RedirectResponse
#
# # =====================================================================================
# # DATABASE
# # =====================================================================================
#
# from sqlalchemy.orm import Session, load_only
# from sqlalchemy import exists, text
# from app.database.base import get_session
#
# # =====================================================================================
# # MODELS
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
# # SCHEMAS
# # =====================================================================================
#
# from app.schemas.payroll_schema import (
#     NotificationStructure,
#     SalaryEnter,
#     SalaryInput,
#     SalaryPolicyCreateSchema,
#     SalaryPolicyUpdateSchema,
#     SalaryPolicyResponseSchema,
#     PolicyComponentPatchSchema,
#     TaxSlabCreateSchema,
#     TaxSlabUpdateSchema,
#     TaxSlabResponseSchema,
# )
#
# # =====================================================================================
# # UTILS – PAYROLL
# # =====================================================================================
#
# from app.utils.payroll_management_utils import (
#
# )
#
# # =====================================================================================
# # NOTIFICATION
# # =====================================================================================
#
# from app.notification.notifications import manager
#
# # =====================================================================================
# # EMAIL
# # =====================================================================================
#
# from app.services.email import send_email_with_attachment
#
# # =====================================================================================
# # S3
# # =====================================================================================
#
# from app.utils.s3_utils import (
#     upload_file_to_s3,
#     generate_http_url,
# )
#
# import boto3
#
# # =====================================================================================
# # AUTH
# # =====================================================================================
#
# from app.utils.authentication import validate_current_role
#
# # =====================================================================================
# # LOGGER
# # =====================================================================================
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# s3_client = boto3.client("s3")
#
# # =====================================================================================
# # ROUTER
# # =====================================================================================
#
# router = APIRouter(tags=["Payroll"])
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# s3_client = boto3.client("s3")
# ##########################################################
# router = APIRouter(tags=["Payroll"])
#
#
# async def _send_payslip_email_async(
#         receiver_email: str,
#         employee_name: str,
#         payslip,
#         password,
#         emp_data: dict
# ) -> Tuple[bool, Optional[str]]:
#     """Send payslip email using existing sendgrid_send_mail(), fetching PDF from DB buffer."""
#
#     SES_USERNAME = os.getenv("SES_USER")
#     SES_PASSWORD = os.getenv("SES_PASS")
#     SMTP_SERVER = os.getenv("SES_HOST")
#     SES_PORT = int(os.getenv("SES_PORT"))
#     FROM_EMAIL = os.getenv("EMAIL_FROM")
#
#     subject = f"Payslip for {calendar.month_name[payslip.month]} {payslip.year}"
#     body = "\n".join([
#         f"Dear {employee_name},",
#         "",
#         f"Your payslip for {calendar.month_name[payslip.month]} {payslip.year} has been generated.",
#         f"Net Salary: ₹{emp_data['net_salary']:,}",
#         f"payslip-password:{password}"
#         "",
#         "Please find your attached payslip PDF.",
#         "",
#         "Regards",
#         "HR Team, SecurXpert Technologies"
#     ])
#
#     # === Check PDF bytes directly from DB (no disk read) ===
#     if not payslip.filedata:
#         return False, "Payslip filedata missing in database; email not sent."
#
#     pdf_bytes = payslip.filedata
#     pdf_filename = payslip.filename or f"{payslip.emp_id}_Payslip_{payslip.month}_{payslip.year}.pdf"  # Convert DB blob to UploadFile for sendgrid_send_mail
#     attachment_file = UploadFile(
#         filename=pdf_filename,
#         file=io.BytesIO(pdf_bytes)
#     )
#
#     try:
#         logger.info(f"📧 Sending payslip email to {receiver_email} for {pdf_filename}")
#
#         await send_email_with_attachment(
#             from_email=FROM_EMAIL,
#             reciver_to=[receiver_email],
#             subject=subject,
#             body=body,
#             body_type="plain",
#             attachment_objs=[attachment_file],
#
#         )
#
#         logger.info(f" Payslip email successfully sent to: {receiver_email}")
#         return True, None
#
#     except Exception as e:
#         logger.error(f" Failed to send payslip email to {receiver_email}: {e}", exc_info=True)
#         return False, str(e)
#
#
# def get_user_role_name(db: Session, employee_id: str) -> str:
#     """
#     Returns role_name for logged-in user
#     """
#     result = (
#         db.query(ProfileInformation.role_name)
#         .join(ProfileInformation, ProfileInformation.role_id == ProfileInformation.role_id)
#         .filter(ProfileInformation.employee_id == employee_id)
#         .first()
#     )
#
#     if not result:
#         raise HTTPException(
#             status_code=403,
#             detail="User role not found"
#         )
#
#     return result[0].lower()  # normalize → hr / manager / admin
#
#
# class ShiftEnum(str, Enum):
#     DAY_SHIFT = "Day_Shift"
#     NIGHT_SHIFT = "Night_Shift"
#     GENERAL_SHIFT = "General_Shift"
#     ROTATIONAL_SHIFT = "Rotational_Shift"
#
#
# class RoleEnum(str, Enum):
#     admin = "Admin"
#     hr = "HR"
#     manager = "Manager"
#     employee = "Employee"
#
#
# @router.post("/Payroll/generate")
# async def generate_salary_excel_sheet_for_total_employees(
#         background_tasks: BackgroundTasks,
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],
#         year: int = Query(..., ge=2000),
#         month: int = Query(..., ge=1, le=12),
#         organization: str = Query(..., description="Organization name (SecurXpert Technologies)"),
#         shift: ShiftEnum = Query(...),
#         db: Session = Depends(get_session),
# ):
#     start_time = time()
#     period_start = date(year, month, 1)
#     period_end = date(year, month, calendar.monthrange(year, month)[1])
#     today = datetime.now()
#     current_year, current_month = today.year, today.month
#
#     prev_month_year = current_year if current_month > 1 else current_year - 1
#     prev_month = current_month - 1 if current_month > 1 else 12
#
#     next_month_year = current_year if current_month < 12 else current_year + 1
#     next_month = current_month + 1 if current_month < 12 else 1
#
#     valid_periods = [
#         (prev_month_year, prev_month),
#         (current_year, current_month),
#         (next_month_year, next_month)
#     ]
#
#     if (year, month) not in valid_periods:
#         raise HTTPException(
#             status_code=400,
#             detail=(
#                 f"Invalid payroll period: {month}-{year}. "
#                 f"Allowed: Previous ({prev_month}-{prev_month_year}), "
#                 f"Current ({current_month}-{current_year}), "
#                 f"Next ({next_month}-{next_month_year})."
#             )
#         )
#
#     #  OPTIMIZATION 1: Fetch PayrollCycle with minimal overhead
#     payroll_cycle = (
#         db.query(PayrollCycle)
#         .filter(PayrollCycle.year == year, PayrollCycle.month == month)
#         .first()
#     )
#
#     #  Prevent regenerate if Approved
#     if payroll_cycle and payroll_cycle.approval_status == "Approved":
#         raise HTTPException(
#             status_code=400,
#             detail=f"Payroll already APPROVED for {calendar.month_name[month]} {year}. Generation not allowed."
#         )
#
#     #  Create payroll cycle if missing
#     if not payroll_cycle:
#         payroll_cycle = PayrollCycle(year=year, month=month, approval_status="Pending")
#         db.add(payroll_cycle)
#         db.commit()
#         db.refresh(payroll_cycle)
#
#     #  OPTIMIZATION 2: Timesheet existence check using EXISTS (fastest)
#     has_timesheet = db.execute(text("""
#         SELECT 1
#         FROM timesheet
#         WHERE week_start_date <= :period_end
#           AND week_end_date >= :period_start
#         LIMIT 1
#     """), {"period_start": period_start, "period_end": period_end}).fetchone()
#
#     # has_timesheet = db.execute(text("""
#     #     SELECT 1 FROM timesheet
#     #     WHERE EXTRACT(YEAR FROM week_start_date) = :year
#     #       AND EXTRACT(MONTH FROM week_start_date) = :month
#     #     LIMIT 1
#     # """), {"year": year, "month": month}).fetchone()
#
#     if not has_timesheet:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No attendance/payroll data found for {calendar.month_name[month]} {year}. "
#                    f"Please generate salary only for months with valid data."
#         )
#
#     #  OPTIMIZATION 3: Fetch ONLY required employee fields
#     employees = (
#         db.query(ProfileInformation)
#         .options(load_only(
#             ProfileInformation.employee_id,
#             ProfileInformation.annual_ctc,
#             ProfileInformation.is_active
#         ))
#         .filter(ProfileInformation.is_active == 1)
#         .all()
#     )
#
#     if not employees:
#         raise HTTPException(status_code=404, detail="No active employees found.")
#
#     all_emp_data, failed_employees, skipped_employees = [], [], []
#
#     for emp in employees:
#         try:
#             #  no rollback here  (Rollback only on exception)
#
#             if not emp.annual_ctc:
#                 failed_employees.append({"employee_id": emp.employee_id, "reason": "Missing annual CTC"})
#                 continue
#
#             #  fetch_timesheet_summary likely queries DB each time
#             # (Optimization can be done separately by fetching all timesheets in one query)
#             timesheet_summary = fetch_timesheet_summary(emp.employee_id, year, month, db)
#
#             if not timesheet_summary:
#                 skipped_employees.append({
#                     "employee_id": emp.employee_id,
#                     "reason": "No timesheet data for this month"
#                 })
#                 continue
#
#             salary_record = SalaryComponentName(
#                 emp_id=emp.employee_id,
#                 annual_ctc=emp.annual_ctc,
#                 year=year,
#                 month=month
#             )
#
#             emp_data = process_salary_and_generate_pdf(
#                 salary_record,
#                 db,
#                 regime="new",
#                 start_date=period_start,
#                 end_date=period_end
#
#             )
#
#             if isinstance(emp_data, dict) and "emp_data" in emp_data:
#                 emp_data = emp_data["emp_data"]
#
#             if emp_data:
#                 all_emp_data.append(emp_data)
#             else:
#                 skipped_employees.append({
#                     "employee_id": emp.employee_id,
#                     "reason": "No valid data (likely missing timesheet)"
#                 })
#
#         except Exception as e:
#             failed_employees.append({"employee_id": emp.employee_id, "reason": str(e)})
#             db.rollback()
#             continue
#
#     #  Generate Excel (placeholder if needed)
#     if not all_emp_data:
#         placeholder_data = [{
#             "Message": "No valid employee data available for this month.",
#             "Year": year,
#             "Month": month,
#             "Generated_On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }]
#         buffer = dump_salary_to_excel(placeholder_data)
#     else:
#         buffer = dump_salary_to_excel(all_emp_data)
#
#     file_data = buffer.getvalue()
#     filename = f"SalarySheet_{year}_{month}.xlsx"
#     s3_url = upload_excel_bytes_to_s3(buffer, filename, folder="payroll_excels")
#
#     params = {
#         "year": year,
#         "month": month,
#         "organization": organization,
#         "shift": shift,
#         "filename": filename,
#         "filedata": file_data,
#         "s3_url": s3_url,
#         "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     }
#
#     insert_sql = text("""
#         INSERT INTO salary_excel_sheets
#           (year, month, organization, shift, filename, filedata, content_type,s3_url)
#         VALUES (:year, :month, :organization, :shift, :filename, :filedata, :content_type,:s3_url)
#     """)
#
#     try:
#         #  OPTIMIZATION 4: Single commit (insert + update payroll cycle)
#         db.execute(insert_sql, params)
#         excel_id = db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
#
#         #  update payroll cycle
#         payroll_cycle.excel_id = excel_id
#         payroll_cycle.generated_date = datetime.utcnow()
#         payroll_cycle.approval_status = "Pending"
#         payroll_cycle.approved_by = None
#         payroll_cycle.approved_at = None
#         payroll_cycle.rejection_reason = None
#
#         db.commit()
#         notification = NotificationSturcture(
#             scenario="Salary Sheet Generated",
#             data={
#                 "message": f"Salary sheet for {calendar.month_name[month]} {year} has been successfully generated."
#             },
#             message="success",
#             timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         )
#
#         await send_notification(emp.employee_id, notification, db)
#
#         #  FIX: Notification should NOT be sent to last "emp.employee_id"
#         # hr_admin_ids = get_employee_ids_by_roles(role_names=["HR", "Admin"], db=db)
#
#         # notification = NotificationSturcture(
#         #     scenario="Salary Sheet Generated",
#         #     data={
#         #         "message": f"Salary sheet for {calendar.month_name[month]} {year} generated and pending approval."
#         #     },
#         #     message="success",
#         #     timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         # )
#
#         # for hr_id in hr_admin_ids:
#         #     background_tasks.add_task(send_notification, hr_id, notification, db)
#
#         # logger.info(f" Notifications sent to HR/Admin for payroll generation {month}-{year}")
#
#     except Exception as e:
#         db.rollback()
#         logger.exception(f" Failed to save Excel record: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to save Excel record: {str(e)}")
#
#     total_time = time() - start_time
#
#     logger.info(
#         f" Salary sheet generated for {len(all_emp_data)} employees "
#         f"(failed: {len(failed_employees)}, skipped: {len(skipped_employees)}) in {total_time:.2f}s"
#     )
#
#     return {
#         "message": (
#             f"Salary sheet generated for {len(all_emp_data)} employees."
#             if all_emp_data else
#             "No valid employee data found — placeholder Excel generated."
#         ),
#         "excel_id": excel_id,
#         "payroll_cycle_id": payroll_cycle.id,
#         "approval_status": payroll_cycle.approval_status,
#         "filename": filename,
#         "organization": organization,
#         "shift": shift,
#         "s3_url": s3_url,  # download link
#         "failed_employees": failed_employees,
#         "skipped_employees": skipped_employees,
#         "processing_time_sec": round(total_time, 2),
#         "current_user": current_user
#     }
#
#
# ###################################
# @router.get("/cycles-list/")
# def list_payroll_cycles(
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],
#         db: Session = Depends(get_session)
# ):
#     cycles = (
#         db.query(PayrollCycle)
#         .order_by(PayrollCycle.year.desc(), PayrollCycle.month.desc())
#         .all()
#     )
#
#     return cycles
#
#
# ###################################################
# @router.post("/Payroll/approve/")
# def approve_payroll(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                     year: int = Query(..., ge=2000),
#                     month: int = Query(..., ge=1, le=12),
#                     db: Session = Depends(get_session)
#                     ):
#     cycle = db.query(PayrollCycle).filter(
#         PayrollCycle.year == year,
#         PayrollCycle.month == month
#     ).first()
#
#     if not cycle:
#         raise HTTPException(status_code=404, detail="Payroll cycle not found")
#
#     if not cycle.excel_id:
#         raise HTTPException(status_code=400, detail="Payroll Excel not generated yet")
#
#     if cycle.approval_status == "Approved":
#         return {"message": "Payroll already approved", "status": cycle.approval_status}
#     current_role = get_user_role_name(db, current_user)
#
#     cycle.approval_status = "Approved"
#     cycle.approved_by = current_role
#     cycle.approved_at = datetime.utcnow()
#     cycle.rejection_reason = None
#     db.commit()
#
#     return {
#         "message": f"Payroll approved for {calendar.month_name[month]} {year}",
#         "status": cycle.approval_status,
#         "excel_id": cycle.excel_id
#     }
#
#
# ######################################################
# @router.post("/Payroll/reject/")
# def reject_payroll(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#
#                    year: int = Query(..., ge=2000),
#                    month: int = Query(..., ge=1, le=12),
#                    reason: str = Query(..., min_length=3),
#                    db: Session = Depends(get_session)
#                    ):
#     cycle = db.query(PayrollCycle).filter(
#         PayrollCycle.year == year,
#         PayrollCycle.month == month
#     ).first()
#
#     if not cycle:
#         raise HTTPException(status_code=404, detail="Payroll cycle not found")
#
#     if not cycle.excel_id:
#         raise HTTPException(status_code=400, detail="Payroll Excel not generated yet")
#     current_role = get_user_role_name(db, current_user)
#
#     cycle.approval_status = "Rejected"
#     cycle.approved_by = current_role
#     cycle.approved_at = datetime.utcnow()
#     cycle.rejection_reason = reason
#     db.commit()
#
#     return {
#         "message": f"Payroll rejected for {calendar.month_name[month]} {year}",
#         "status": cycle.approval_status,
#         "reason": reason,
#         "excel_id": cycle.excel_id
#     }
#
#
# ##############new-end-point
# @router.get("/Payroll/downloads-checking-for-approval/")
# def download_salary_excel_for_approval_stream(
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],  # validate_current_role("admin")
#         excel_id: int = Query(None),
#         year: int = Query(None),
#         month: int = Query(None),
#         db: Session = Depends(get_session)
# ):
#     """
#      Download salary excel sheet from S3 (streaming)
#      No approval restriction (used before approval)
#     """
#     try:
#         if excel_id:
#             query = text("""
#                 SELECT filename, s3_url, content_type
#                 FROM salary_excel_sheets
#                 WHERE id = :id
#             """)
#             params = {"id": excel_id}
#
#         elif year and month:
#             query = text("""
#                 SELECT filename, s3_url, content_type
#                 FROM salary_excel_sheets
#                 WHERE year = :year AND month = :month
#                 ORDER BY id DESC
#                 LIMIT 1
#             """)
#             params = {"year": year, "month": month}
#
#         else:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Provide excel_id OR both year and month."
#             )
#
#         result = db.execute(query, params).fetchone()
#         if not result:
#             raise HTTPException(status_code=404, detail="Salary Excel sheet not found.")
#
#         filename, s3_url, content_type = result
#
#         if not s3_url:
#             raise HTTPException(status_code=404, detail="s3_url not found. File not uploaded to S3.")
#
#         key = url_to_key(s3_url)
#
#         #  Fetch S3 object stream
#
#         obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
#         file_stream = obj["Body"]
#
#         headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
#
#         return StreamingResponse(
#             file_stream,
#             media_type=content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers=headers
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.exception(f"S3 streaming download failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to download Excel: {str(e)}")
#
#
# ######################################updated-router
# @router.get("/Payroll/downloads/")
# def download_salary_excel_only_if_approved_stream(
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],  # validate_current_role("admin")
#         excel_id: int = Query(None),
#         year: int = Query(None),
#         month: int = Query(None),
#         db: Session = Depends(get_session)
# ):
#     """
#      Download salary excel sheet from S3 (streaming)
#      Only allowed if payroll is Approved
#     """
#     try:
#         if not excel_id and not (year and month):
#             raise HTTPException(status_code=400, detail="Provide excel_id OR both year and month.")
#
#         #  Check payroll approval
#         if excel_id:
#             cycle = db.execute(text("""
#                 SELECT year, month, approval_status
#                 FROM payroll_cycles
#                 WHERE excel_id = :excel_id
#                 ORDER BY id DESC
#                 LIMIT 1
#             """), {"excel_id": excel_id}).fetchone()
#
#             if not cycle:
#                 raise HTTPException(status_code=404, detail="Payroll cycle not found.")
#
#             cycle_year, cycle_month, approval_status = cycle
#
#         else:
#             cycle = db.execute(text("""
#                 SELECT approval_status
#                 FROM payroll_cycles
#                 WHERE year = :year AND month = :month
#                 ORDER BY id DESC
#                 LIMIT 1
#             """), {"year": year, "month": month}).fetchone()
#
#             if not cycle:
#                 raise HTTPException(status_code=404, detail=f"Payroll cycle not found for {month}-{year}")
#
#             approval_status = cycle[0]
#             cycle_year, cycle_month = year, month
#
#         if approval_status != "Approved":
#             raise HTTPException(
#                 status_code=403,
#                 detail=f"Payroll not approved for {cycle_month}-{cycle_year}. Current status: {approval_status}"
#             )
#
#         #  Fetch Salary Excel sheet from DB
#         if excel_id:
#             query = text("""
#                 SELECT filename, s3_url, content_type
#                 FROM salary_excel_sheets
#                 WHERE id = :id
#             """)
#             params = {"id": excel_id}
#         else:
#             query = text("""
#                 SELECT filename, s3_url, content_type
#                 FROM salary_excel_sheets
#                 WHERE year = :year AND month = :month
#                 ORDER BY id DESC
#                 LIMIT 1
#             """)
#             params = {"year": year, "month": month}
#
#         result = db.execute(query, params).fetchone()
#         if not result:
#             raise HTTPException(status_code=404, detail="Salary Excel sheet not found.")
#
#         filename, s3_url, content_type = result
#
#         if not s3_url:
#             raise HTTPException(status_code=404, detail="s3_url not found. File not uploaded to S3.")
#
#         key = url_to_key(s3_url)
#
#         #  S3 streaming response
#         obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
#         file_stream = obj["Body"]
#
#         headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
#
#         return StreamingResponse(
#             file_stream,
#             media_type=content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers=headers
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.exception(f"S3 streaming download failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to download Excel: {str(e)}")
#
#
# ##################################################
# # 3. Upload Optional Excel
# @router.post("/Payroll/upload")
# async def upload_salary_excel_sheet_in_database_optional(
#         organization: str = Form(...),
#         shift: str = Form(...),
#         year: int = Form(...),
#         month: int = Form(...),
#         file: UploadFile = File(...),
#         db: Session = Depends(get_session)
# ):
#     if not file.filename.endswith(".xlsx"):
#         raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")
#
#     file_data = await file.read()
#
#     salary_sheet = SalaryExcelSheet(
#         organization=organization,
#         shift=shift,
#         year=year,
#         month=month,
#         filename=file.filename,
#         filedata=file_data,
#         content_type=file.content_type
#     )
#     db.add(salary_sheet)
#     db.commit()
#
#     return {
#         "message": "Excel file uploaded successfully.",
#         "id": salary_sheet.id,
#         "filename": salary_sheet.filename
#     }
#
#
# ############################################################
# def generate_emp_data_and_pdf(
#         emp_id: str,
#         month: int,
#         year: int,
#         total_ctc: float,
#         db: Session,
#         regime: str = "new",
#         arrears: float = 0.0,
#         bonus: float = 0.0,
#         reimbursements: float = 0.0,
#         other_deductions: float = 0.0,
# ) -> Tuple[Dict, bytes]:
#     """
#      Uses your existing utils:
#     1) process_salary_and_generate_pdf -> returns emp_data (dict) and saves SalaryComponentName
#     2) generate_payslip_pdf(emp_data) -> returns pdf_bytes
#
#     Returns:
#         emp_data (dict), pdf_bytes (bytes)
#     """
#
#     data = SalaryComponentName(
#         emp_id=emp_id,
#         month=month,
#         year=year,
#         annual_ctc=total_ctc
#     )
#
#     emp_data = process_salary_and_generate_pdf(
#         data=data,
#         db=db,
#         regime=regime,
#         arrears=arrears,
#         bonus=bonus,
#         reimbursements=reimbursements,
#         other_deductions_param=other_deductions,
#     )
#     password = generate_password(emp_data)
#
#     pdf_bytes = generate_payslip_pdf(emp_data)
#
#     return emp_data, pdf_bytes, password
#
#
# ####################payslip-generation-router
# @router.post("/Payroll/generate-payslips")
# async def generate_payslips(
#         background_tasks: BackgroundTasks,
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],
#         excel_file: UploadFile = File(...),
#         month: int = Query(..., ge=1, le=12),
#         year: int = Query(..., ge=1900),
#         db: Session = Depends(get_session),
# ):
#     """
#      Payslips will be generated ONLY if PayrollCycle is APPROVED.
#      Optimized queries: bulk employee + bonus fetch, bulk insert payslips.
#     """
#
#     start_time = time()
#
#     #  1) PayrollCycle APPROVAL validation (MANDATORY)
#     cycle = db.query(PayrollCycle).filter(
#         PayrollCycle.year == year,
#         PayrollCycle.month == month
#     ).first()
#
#     if not cycle:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Payroll cycle not found for {month}-{year}. Generate payroll sheet first."
#         )
#
#     if cycle.approval_status != "Approved":
#         raise HTTPException(
#             status_code=403,
#             detail=f"Payroll not approved for {month}-{year}. Current status: {cycle.approval_status}"
#         )
#
#     #  2) Read excel safely
#     try:
#         contents = await excel_file.read()
#         df = pd.read_excel(BytesIO(contents), engine="openpyxl")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error reading Excel file: {e}")
#
#     #  3) Validate payslip_month column
#     if "payslip_month" not in df.columns:
#         raise HTTPException(
#             status_code=400,
#             detail="Missing 'payslip_month' column in Excel. Expected 'MM-YYYY' or 'Month YYYY'."
#         )
#
#     payslip_month_value = str(df["payslip_month"].dropna().iloc[0]).strip()
#
#     # Accept MM-YYYY or Month YYYY formats
#     if re.match(r"^(0[1-9]|1[0-2])-\d{4}$", payslip_month_value):
#         excel_month, excel_year = map(int, payslip_month_value.split("-"))
#     else:
#         try:
#             parsed_date = datetime.strptime(payslip_month_value, "%B %Y")
#             excel_month, excel_year = parsed_date.month, parsed_date.year
#         except ValueError:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Invalid payslip_month. Use 'MM-YYYY' (e.g., 09-2025) or 'Month YYYY' (e.g., September 2025)."
#             )
#
#     if excel_month != month or excel_year != year:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Excel payslip_month ({payslip_month_value}) does not match requested {month}-{year}."
#         )
#
#     #  4) Utility functions
#     def safe_str(value):
#         if not value:
#             return None
#         if isinstance(value, dict):
#             return value.get("company") or value.get("personal") or next(iter(value.values()), None)
#         if isinstance(value, str):
#             return value.strip()
#         return str(value)
#
#     #  5) Extract all emp_ids from excel
#     excel_emp_ids = [
#         safe_str(x) for x in df.get("emp_id", []).tolist()
#         if safe_str(x)
#     ]
#     excel_emp_ids = list(set(excel_emp_ids))  # unique IDs
#
#     if not excel_emp_ids:
#         raise HTTPException(status_code=400, detail="Excel contains no valid emp_id values.")
#
#     total_days = calendar.monthrange(year, month)[1]
#
#     #  OPTIMIZATION 1: Bulk fetch Employees in ONE query
#     employees = db.query(ProfileInformation).filter(
#         ProfileInformation.employee_id.in_(excel_emp_ids)
#     ).all()
#
#     employee_map = {e.employee_id: e for e in employees}
#
#     #  OPTIMIZATION 2: Bulk fetch Bonuses in ONE query
#     bonuses = db.query(Bonus).filter(
#         Bonus.employee_id.in_(excel_emp_ids)
#     ).all()
#     bonus_map = {b.employee_id: float(b.amount) for b in bonuses}
#
#     #  OPTIMIZATION 3: Prevent duplicate payslip generation (optional)
#     existing_payslips = db.query(Payslip.emp_id).filter(
#         Payslip.emp_id.in_(excel_emp_ids),
#         Payslip.year == year,
#         Payslip.month == month
#     ).all()
#     existing_emp_ids = set([x[0] for x in existing_payslips])
#
#     all_results = []
#     payslips_to_insert = []
#
#     for index, row in df.iterrows():
#         emp_id = safe_str(row.get("emp_id"))
#         if not emp_id:
#             all_results.append({"row_index": index + 1, "status": "failed", "reason": "Missing emp_id"})
#             continue
#
#         if emp_id in existing_emp_ids:
#             all_results.append({"employee_id": emp_id, "status": "skipped", "reason": "Payslip already exists"})
#             continue
#
#         employee = employee_map.get(emp_id)
#         if not employee:
#             all_results.append({"employee_id": emp_id, "status": "failed", "reason": "Employee not found in DB"})
#             continue
#
#         bonus_amount = bonus_map.get(emp_id, 0.0)
#
#         emp_email = safe_str(employee.email)
#         emp_name = f"{safe_str(employee.first_name)} {safe_str(employee.last_name)}"
#
#         total_ctc = row.get("total_ctc")
#         if total_ctc is None:
#             all_results.append({"employee_id": emp_id, "status": "failed", "reason": "Missing annual_ctc"})
#             continue
#
#         try:
#             #  Generate PDF
#             bonus_amount = bonus_map.get(emp_id, 0.0)
#
#             #  ONLY CALL UTILS HERE (No emp_data build in router)
#             emp_data, pdf_bytes, password = generate_emp_data_and_pdf(
#                 emp_id=emp_id,
#                 month=month,
#                 year=year,
#                 total_ctc=float(total_ctc),
#                 bonus=float(bonus_amount),
#                 db=db,
#                 regime="new"
#             )
#
#             payslip_obj = Payslip(
#                 emp_id=emp_id,
#                 year=year,
#                 month=month,
#                 filename=f"{emp_id}_Payslip_{month}_{year}.pdf",
#                 filedata=pdf_bytes,
#                 content_type="application/pdf",
#                 status="generated",
#                 approved_at=datetime.utcnow(),  # because payroll already approved
#             )
#
#             payslips_to_insert.append(payslip_obj)
#
#             #  Send email via background task (fast)
#             if emp_email:
#                 background_tasks.add_task(
#                     _send_payslip_email_async,
#                     receiver_email=emp_email,
#                     employee_name=emp_name,
#                     payslip=payslip_obj,
#                     emp_data=emp_data,
#                     password=password
#
#                 )
#
#             all_results.append({
#                 "employee_id": emp_id,
#                 "status": "success",
#                 "net_salary": emp_data["net_salary"],
#                 "message": "Payslip generated (email queued)"
#             })
#             notify_data = {
#                 "scenario": "Payslip Generated",
#                 "data": {
#                     "details": f"Employee {employee.first_name} {employee.last_name} payslip month and year  {year}{month}."
#                 },
#                 "message": f"Your payslip for {datetime(year, month, 1).strftime('%B %Y')} is ready. Net Salary: ₹{emp_data['net_salary']}",
#             }
#
#             notify_schemas = NotificationSturcture(**notify_data)
#
#             # ---------------- Send Notification to HR ----------------
#             background_tasks.add_task(
#                 send_notification,
#                 employee.employee_id,
#                 notification_data=notify_schemas,
#                 db=db
#             )
#
#         except Exception as e:
#             all_results.append({"employee_id": emp_id, "status": "failed", "reason": str(e)})
#
#     #  OPTIMIZATION 4: Bulk insert Payslips (ONE commit)
#     try:
#         if payslips_to_insert:
#             db.bulk_save_objects(payslips_to_insert)
#             db.commit()
#         else:
#             db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to save payslips: {str(e)}")
#
#     success_count = sum(1 for r in all_results if r["status"] == "success")
#     failed_count = sum(1 for r in all_results if r["status"] == "failed")
#     skipped_count = sum(1 for r in all_results if r["status"] == "skipped")
#
#     total_time = time() - start_time
#
#     return {
#         "message": (
#             f"Payslip generation completed for {len(df)} rows. "
#             f"Success: {success_count}, Failed: {failed_count}, Skipped: {skipped_count}"
#         ),
#         "payroll_cycle": {
#             "year": year,
#             "month": month,
#             "status": cycle.approval_status,
#             "excel_id": cycle.excel_id
#         },
#         "processing_time_sec": round(total_time, 2),
#         "results": all_results
#     }
#
#
# ######################################################
# @router.get("/employee/{emp_id}/payslip/{year}/{month}")
# def employee_download_payslip(emp_id: str, year: int, month: int,
#                               current_user: Annotated[str, Depends(validate_current_role("employee"))],
#                               db: Session = Depends(get_session),
#                               ):
#     """
#     Download a generated payslip PDF for a given employee, year, and month.
#     Automatically logs this action in the payslip_actions table.
#     """
#     logged_emp_id = current_user  # if current_user is already employee_id
#
#     # ✅ 2) Ownership validation
#     if logged_emp_id != emp_id:
#         raise HTTPException(status_code=403, detail="Access denied. You can download only your own payslip.")
#     # Step 1: Fetch the payslip from DB
#     payslip = db.query(Payslip).filter(
#         Payslip.emp_id == emp_id,
#         Payslip.year == year,
#         Payslip.month == month
#     ).first()
#
#     if not payslip:
#         raise HTTPException(status_code=404, detail="Payslip not found. Make sure it was generated.")
#
#     current_name = get_user_role_name(db, current_user)
#     # Step 2: Log the download action in payslip_actions
#     new_action = PayslipAction(
#         emp_id=emp_id,
#         filename=payslip.filename or f"{emp_id}_Payslip_{year}_{month}.pdf",
#         action_by=current_name,  # You can change this to admin username if needed
#         action_type="downloaded",
#         timestamp=datetime.utcnow()
#     )
#     db.add(new_action)
#     db.commit()
#
#     # Step 3: Serve PDF as StreamingResponse
#     file_stream = BytesIO(payslip.filedata)
#     filename = payslip.filename or f"{emp_id}_Payslip_{year}_{month}.pdf"
#     content_type = payslip.content_type or "application/pdf"
#
#     return StreamingResponse(
#         file_stream,
#         media_type=content_type,
#         headers={"Content-Disposition": f"attachment; filename={filename}"}
#     )
#
#
# @router.get("/admin/{emp_id}/payslip/{year}/{month}")
# def admin_download_payslip(emp_id: str, year: int, month: int,
#                            current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                            db: Session = Depends(get_session),
#                            ):
#     """
#     Download a generated payslip PDF for a given employee, year, and month.
#     Automatically logs this action in the payslip_actions table.
#     """
#     # Step 1: Fetch the payslip from DB
#     payslip = db.query(Payslip).filter(
#         Payslip.emp_id == emp_id,
#         Payslip.year == year,
#         Payslip.month == month
#     ).first()
#
#     if not payslip:
#         raise HTTPException(status_code=404, detail="Payslip not found. Make sure it was generated.")
#
#     # Step 2: Log the download action in payslip_actions
#     new_action = PayslipAction(
#         emp_id=emp_id,
#         filename=payslip.filename or f"{emp_id}_Payslip_{year}_{month}.pdf",
#         action_by=emp_id,  # You can change this to admin username if needed
#         action_type="downloaded",
#         timestamp=datetime.utcnow()
#     )
#     db.add(new_action)
#     db.commit()
#
#     # Step 3: Serve PDF as StreamingResponse
#     file_stream = BytesIO(payslip.filedata)
#     filename = payslip.filename or f"{emp_id}_Payslip_{year}_{month}.pdf"
#     content_type = payslip.content_type or "application/pdf"
#
#     return StreamingResponse(
#         file_stream,
#         media_type=content_type,
#         headers={"Content-Disposition": f"attachment; filename={filename}"}
#     )
#
#
# @router.get("/employee/payslip/action-history")
# def get_payslip_action_history(
#         current_user: Annotated[str, Depends(validate_current_role("admin"))],
#         emp_id: str = Query(..., description="Employee ID to view payslip access history"),
#         db: Session = Depends(get_session)
# ):
#     actions = (
#         db.query(PayslipAction)
#         .filter(PayslipAction.emp_id == emp_id)
#         .order_by(PayslipAction.timestamp.desc())
#         .all()
#     )
#
#     if not actions:
#         raise HTTPException(status_code=404, detail="No payslip actions found for this employee.")
#
#     return [
#         {
#             "filename": action.filename,
#             "action_by": action.action_by,
#             "action_type": action.action_type,
#             "timestamp": action.timestamp
#         }
#         for action in actions
#     ]
#
#
# ####################################################
# @router.post("/salary_component/add")
# def add_salary_components(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                           payload: salryenter, db: Session = Depends(get_session)):
#     # Check if employee salary already exists
#     existing = db.query(Salary_components).filter(
#         Salary_components.emp_id == payload.emp_id
#     ).first()
#     if existing:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Salary components for employee {payload.emp_id} already exist.",
#         )
#
#     #  Correct parameter order
#     components = compute_salary_components(
#         payload.annual_ctc, payload.emp_id, payload.regime, db
#     )
#
#     # Add new record
#     new_salary = Salary_components(
#         emp_id=payload.emp_id,
#         annual_ctc=payload.annual_ctc,
#         regime=payload.regime,
#         **components,
#     )
#     db.add(new_salary)
#     db.commit()
#
#     return {"status": "success", "data": new_salary}
#
#
# @router.get("/salary_components", response_model=List[SalaryInput])
# def get_all_salary_components(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                               db: Session = Depends(get_session)):
#     data = db.query(Salary_components).all()
#     return data
#
#
# @router.get("/salary_component/{emp_id}", response_model=SalaryInput)
# def get_salary_by_emp_id(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                          emp_id: str, db: Session = Depends(get_session)):
#     record = db.query(Salary_components).filter(
#         Salary_components.emp_id == emp_id
#     ).first()
#     if not record:
#         raise HTTPException(
#             status_code=404, detail="Salary components not found for given emp_id"
#         )
#     return record
#
#
# @router.put("/salary_component/update/{emp_id}")
# def update_salary_components(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                              emp_id: str, payload: salryenter, db: Session = Depends(get_session)):
#     record = db.query(Salary_components).filter(
#         Salary_components.emp_id == emp_id
#     ).first()
#
#     if not record:
#         raise HTTPException(
#             status_code=404, detail="Salary components not found for given emp_id"
#         )
#
#     # Fixed parameter order + added db
#     updated_components = compute_salary_components(
#         payload.annual_ctc, emp_id, payload.regime, db
#     )
#
#     record.annual_ctc = payload.annual_ctc
#     record.regime = payload.regime
#
#     for key, value in updated_components.items():
#         setattr(record, key, value)
#
#     db.commit()
#     db.refresh(record)
#
#     return {"status": "success", "data": record}
#
#
# # ---------------- Salary Policy ----------------
#
# @router.get(
#     "/policy",
#     response_model=List[SalaryPolicyResponseSchema]
# )
# def get_salary_policies(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                         policy_id: Optional[int] = Query(
#                             None,
#                             description="Provide policy_id to fetch a specific policy"
#                         ),
#                         db: Session = Depends(get_session),
#                         ):
#     if policy_id:
#         # policy = db.query(SalaryPolicy1).filter(
#         #     SalaryPolicy1.id == policy_id
#         # ).first()
#         policy = db.query(exists().where(SalaryPolicy1.id == policy_id)).scalar()
#
#         if not policy:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Salary policy not found"
#             )
#
#         # Return as list to match response_model
#         return [policy]
#
#     # If no policy_id → return all
#     return db.query(SalaryPolicy1).all()
#
#
# ########################################
#
# @router.post(
#     "/policy",
#     response_model=SalaryPolicyResponseSchema,
#     status_code=status.HTTP_201_CREATED
# )
# def create_salary_policy(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                          payload: SalaryPolicyCreateSchema,
#                          db: Session = Depends(get_session)
#                          ):
#     try:
#         #  OPTIMIZATION 1: Use EXISTS (fast check, does not load full row)
#         overlap_exists = db.query(
#             exists().where(
#                 SalaryPolicy1.is_active == True,
#                 SalaryPolicy1.salary_range["min_annual_ctc"].as_integer()
#                 <= payload.salary_range.max_annual_ctc,
#                 SalaryPolicy1.salary_range["max_annual_ctc"].as_integer()
#                 >= payload.salary_range.min_annual_ctc,
#             )
#         ).scalar()
#
#         if overlap_exists:
#             raise HTTPException(
#                 status_code=400,
#                 detail="An active salary policy already exists for this CTC range"
#             )
#
#         #  Create policy (no temp salary_sheet_id logic with 2 commits)
#         policy = SalaryPolicy1(
#             salary_sheet_id="TEMP",  # placeholder initially
#             effective_from=payload.effective_from,
#             is_active=payload.is_active,
#             salary_range=payload.salary_range.dict(),
#             components=[c.dict() for c in payload.components],
#         )
#
#         db.add(policy)
#
#         #  OPTIMIZATION 2: Flush to get policy.id without committing
#         db.flush()
#
#         #  Generate salary_sheet_id after ID exists (still same transaction)
#         year = policy.effective_from.year
#         policy.salary_sheet_id = f"SAL-{year}-{str(policy.id).zfill(4)}"
#
#         #  OPTIMIZATION 3: Only ONE commit
#         db.commit()
#         db.refresh(policy)
#
#         return policy
#
#     except HTTPException:
#         db.rollback()
#         raise
#
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )
#
#
# ###################################################
# @router.put(
#     "/policy/{policy_id}",
#     response_model=SalaryPolicyResponseSchema,
#     description="""
#  Update Salary Policy (Full Update)
#
# This endpoint updates a salary policy by replacing the given fields.
# - `salary_sheet_id` cannot be modified.
# - `components` accepts list of earning/deduction salary components.
# - Use this when you want to update full policy structure.
# """
# )
# def update_salary_policy(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                          policy_id: int,
#                          payload: SalaryPolicyUpdateSchema = Body(
#                              example={
#                                  "effective_from": "2026-01-19",
#                                  "is_active": True,
#                                  "salary_range": {
#                                      "min_annual_ctc": 500000,
#                                      "max_annual_ctc": 800000,
#                                      "currency": "INR"
#                                  },
#                                  "components": [
#                                      {
#                                          "component_name": "basic_salary",
#                                          "percentage": 50,
#                                          "type": "earning",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "hra",
#                                          "percentage": 50,
#                                          "type": "earning",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "food_allowance",
#                                          "percentage": 15,
#                                          "type": "earning",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "special_allowance",
#                                          "percentage": 15,
#                                          "type": "earning",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "other_allowance",
#                                          "percentage": 20,
#                                          "type": "earning",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "pf_employee",
#                                          "percentage": 12,
#                                          "type": "deductions",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "pf_employer",
#                                          "percentage": 12,
#                                          "type": "deductions",
#                                          "calculation_type": "percentage"
#                                      },
#                                      {
#                                          "component_name": "professional_tax",
#                                          "percentage": 200,
#                                          "type": "deductions",
#                                          "calculation_type": "fixed"
#                                      },
#                                      {
#                                          "component_name": "health_insurance",
#                                          "percentage": 185,
#                                          "type": "deductions",
#                                          "calculation_type": "fixed"
#                                      }
#                                  ]
#                              }
#                          ),
#                          db: Session = Depends(get_session),
#                          ):
#     policy = db.query(SalaryPolicy1).filter(SalaryPolicy1.id == policy_id).first()
#     # policy=db.query( exists().where(SalaryPolicy1.id == policy_id)).scalar()
#
#     if not policy:
#         raise HTTPException(status_code=404, detail="Salary policy not found")
#
#     update_data = payload.dict(exclude_unset=True)
#
#     #  Never allow system field update
#     update_data.pop("salary_sheet_id", None)
#
#     if "effective_from" in update_data:
#         policy.effective_from = update_data["effective_from"]
#
#     if "is_active" in update_data:
#         policy.is_active = update_data["is_active"]
#
#     if "salary_range" in update_data:
#         policy.salary_range = update_data["salary_range"]
#
#     if "components" in update_data:
#         policy.components = update_data["components"]
#
#     policy.updated_at = datetime.utcnow()
#
#     db.commit()
#     db.refresh(policy)
#
#     return policy
#
#
# ##############################################################
# @router.patch("/policy/{policy_id}/component/{component_name}")
# def patch_policy_component(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                            policy_id: int,
#                            component_name: str,
#                            payload: PolicyComponentPatchSchema,
#                            db: Session = Depends(get_session),
#                            ):
#     policy = db.query(SalaryPolicy1).filter(SalaryPolicy1.id == policy_id).first()
#     # policy=db.query(exists().where(SalaryPolicy1.id == policy_id)).scalar()
#
#     if not policy:
#         raise HTTPException(status_code=404, detail="Salary policy not found")
#
#     if not policy.components or not isinstance(policy.components, list):
#         raise HTTPException(status_code=400, detail="components missing or invalid")
#
#     patch_data = payload.dict(exclude_unset=True)
#
#     #  Copy list (force SQLAlchemy update)
#     components_copy = copy.deepcopy(policy.components)
#
#     updated = False
#     for comp in components_copy:
#         #  strict match
#         if str(comp.get("component_name")).strip().lower() == component_name.strip().lower():
#             for k, v in patch_data.items():
#                 comp[k] = v
#             updated = True
#             break
#
#     if not updated:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Component '{component_name}' not found in policy components"
#         )
#
#     #  reassign
#     policy.components = components_copy
#     policy.updated_at = datetime.utcnow()
#
#     db.commit()
#     db.refresh(policy)
#
#     return {"status": "success", "data": policy}
#
#
# ##########################################################
# @router.delete(
#     "/policy/{policy_id}",
#     status_code=200
# )
# def delete_salary_policy(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                          policy_id: int,
#                          db: Session = Depends(get_session)
#                          ):
#     policy = db.query(SalaryPolicy1).filter(
#         SalaryPolicy1.id == policy_id
#     ).first()
#     policy = db.query(exists().where(SalaryPolicy1.id == policy_id)).scalar()
#
#     if not policy:
#         raise HTTPException(
#             status_code=404,
#             detail="Salary policy not found"
#         )
#
#     db.delete(policy)
#     db.commit()
#
#     return {
#         "detail": f"Salary policy '{policy.salary_sheet_id}' deleted successfully"
#     }
#
#
# # ---------------- Tax Slabs ----------------
#
# @router.get(
#     "/slabs",
#     response_model=List[TaxSlabResponseSchema],
# )
# def get_tax_slabs(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                   slab_id: Optional[str] = Query(
#                       None, description="Provide slab_id (e.g. SLAB001) to fetch specific slab"
#                   ),
#                   db: Session = Depends(get_session),
#                   ):
#     if slab_id:
#         # slab = db.query(TaxSlab1).filter(TaxSlab1.slab_id == slab_id).first()
#         slab = db.query(exists().where(TaxSlab1.slab_id == slab_id)).scalar()
#
#         if not slab:
#             raise HTTPException(status_code=404, detail="Tax slab not found")
#         return [slab]
#
#     return db.query(TaxSlab1).all()
#
#
# def generate_slab_id(db: Session) -> str:
#     """
#     Generate slab_id like SLAB001, SLAB002, ...
#     """
#     last_slab = (
#         db.query(TaxSlab1)
#         .order_by(TaxSlab1.id.desc())
#         .first()
#     )
#
#     if not last_slab or not last_slab.slab_id:
#         return "SLAB001"
#
#     last_number = int(last_slab.slab_id.replace("SLAB", ""))
#     return f"SLAB{last_number + 1:03d}"
#
#
# #################################################################
# @router.post(
#     "/slabs",
#     response_model=TaxSlabResponseSchema
# )
# def create_tax_slab(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                     payload: TaxSlabCreateSchema,
#                     db: Session = Depends(get_session),
#                     ):
#     slab = TaxSlab1(
#         slab_id=generate_slab_id(db),
#         regime=payload.regime,
#         slab_ranges=[s.dict() for s in payload.slab_ranges],  # LIST JSON
#         effective_from=payload.effective_from,
#         is_active=payload.is_active,
#     )
#
#     db.add(slab)
#     db.commit()
#     db.refresh(slab)
#
#     return slab
#
#
# #################################################################
# @router.put(
#     "/slabs/{slab_id}",
#     response_model=TaxSlabResponseSchema, description="""{
#   "regime": "old",
#   "slab_ranges": [
#     {
#       "lower_limit": 0,
#       "upper_limit": 400000,
#       "rate": 0
#     },
#      {
#       "lower_limit": 400001,
#       "upper_limit": 800000,
#       "rate": 0.05
#     },
#
#      {
#       "lower_limit": 800001,
#       "upper_limit": 1200000,
#       "rate": 0.1
#     },
#     {
#       "lower_limit": 1200001,
#       "upper_limit": 1600000,
#       "rate": 0.15
#     },
#      {
#       "lower_limit": 1600001,
#       "upper_limit": 2000000,
#       "rate": 0.2
#     },
#      {
#       "lower_limit": 2000001,
#       "upper_limit": 2400000,
#       "rate": 0.25
#     },
#      {
#       "lower_limit": 2400001,
#       "upper_limit": 10000000,
#       "rate": 0.3
#     }
#   ],
#   "effective_from": "2026-01-19",
#   "is_active": 1
# }"""
# )
# def update_tax_slab(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                     slab_id: str,
#                     payload: TaxSlabUpdateSchema = Body(example={
#                         "regime": "new",
#                         "slab_ranges": [
#                             {
#                                 "lower_limit": 0,
#                                 "upper_limit": 1200000,
#                                 "rate": 0
#                             },
#                             {
#                                 "lower_limit": 1200001,
#                                 "upper_limit": 1600000,
#                                 "rate": 0.15
#                             },
#                             {
#                                 "lower_limit": 1600001,
#                                 "upper_limit": 2000000,
#                                 "rate": 0.2
#                             },
#                             {
#                                 "lower_limit": 2000001,
#                                 "upper_limit": 2400000,
#                                 "rate": 0.25
#                             },
#                             {
#                                 "lower_limit": 2400000,
#                                 "upper_limit": 10000000,
#                                 "rate": 0.3
#                             }
#                         ],
#                         "effective_from": "2026-01-19",
#                         "is_active": 1
#                     }, ),
#                     db: Session = Depends(get_session),
#                     ):
#     slab = db.query(TaxSlab1).filter(TaxSlab1.slab_id == slab_id).first()
#     # slab = db.query(exists().where(TaxSlab1.slab_id == slab_id)).scalar()
#
#     if not slab:
#         raise HTTPException(status_code=404, detail="Tax slab not found")
#
#     if payload.regime is not None:
#         slab.regime = payload.regime
#
#     if payload.slab_ranges is not None:
#         slab.slab_ranges = [s.dict() for s in payload.slab_ranges]
#
#     if payload.effective_from is not None:
#         slab.effective_from = payload.effective_from
#
#     if payload.is_active is not None:
#         slab.is_active = payload.is_active
#
#     db.commit()
#     db.refresh(slab)
#     return slab
#
#
# #################################################
# @router.delete(
#     "/slabs/{slab_id}",
#
# )
# def delete_tax_slab(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                     slab_id: str,
#                     db: Session = Depends(get_session),
#                     ):
#     slab = db.query(exists().where(TaxSlab1.slab_id == slab_id)).scalar()
#     if not slab:
#         raise HTTPException(status_code=404, detail="Tax slab not found")
#
#     db.delete(slab)
#     db.commit()
#     return {"message": f"Tax slab '{slab_id}' deleted successfully"}
#
#
# #########################################****************************
# @router.post("/arrears/submit")
# def submit_arrear(
#         current_user: Annotated[str, Depends(validate_current_role("employee"))],
#         employee_id: str = Form(...),
#         month: int = Form(...),
#         year: int = Form(...),
#         amount: float = Form(...),
#         type: ArrearType = Form(...),
#         reason: str = Form(None),
#         db: Session = Depends(get_session)
# ):
#     # Check employee exists
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     arrear = Arrear(
#         employee_id=employee_id,
#         month=month,
#         year=year,
#         amount=amount,
#         type=type,
#         reason=reason
#     )
#     db.add(arrear)
#     db.commit()
#     db.refresh(arrear)
#     return {"message": "Arrear submitted successfully", "arrear_id": arrear.id}
#
#
# @router.get("/arrears/{employee_id}")
# def list_arrears(employee_id: str, current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                  db: Session = Depends(get_session)):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     arrears = db.query(Arrear).filter(Arrear.employee_id == employee_id).all()
#     return [{"id": a.id, "month": a.month, "year": a.year, "amount": a.amount, "type": a.type.value, "reason": a.reason}
#             for a in arrears]
#
#
# # ------------------ Bonuses Submission ------------------
# @router.post("/bonuses/submit")
# def submit_bonus(current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                  employee_id: str = Form(...),
#                  month: int = Form(...),
#                  year: int = Form(...),
#                  amount: float = Form(...),
#                  type: BonusType = Form(...),
#                  remarks: str = Form(None),
#                  db: Session = Depends(get_session)
#                  ):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     bonus = Bonus(
#         employee_id=employee_id,
#         month=month,
#         year=year,
#         amount=amount,
#         type=type,
#         remarks=remarks
#     )
#     db.add(bonus)
#     db.commit()
#     db.refresh(bonus)
#     return {"message": "Bonus submitted successfully", "bonus_id": bonus.id}
#
#
# @router.get("/bonuses/{employee_id}")
# def list_bonuses(employee_id: str, current_user: Annotated[str, Depends(validate_current_role("employee"))],
#                  db: Session = Depends(get_session)):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     bonuses = db.query(Bonus).filter(Bonus.employee_id == employee_id).all()
#     return [
#         {"id": b.id, "month": b.month, "year": b.year, "amount": b.amount, "type": b.type.value, "remarks": b.remarks}
#         for b in bonuses]
#
#
# @router.get("/bonuses/{employee_id}")
# def admin_get_bonus_details(employee_id: str, current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                             db: Session = Depends(get_session)):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     bonuses = db.query(Bonus).filter(Bonus.employee_id == employee_id).all()
#     return [
#         {"id": b.id, "month": b.month, "year": b.year, "amount": b.amount, "type": b.type.value, "remarks": b.remarks}
#         for b in bonuses]
#
#
# # ------------------ Expense Claims Submission ------------------
# @router.post("/expenses/submit")
# def submit_expense(
#         current_user: Annotated[str, Depends(validate_current_role(""))],
#         employee_id: str = Form(...),
#         expenses_type: ExpenseType = Form(...),
#         bill_number: str = Form(...),
#         amount: float = Form(...),
#         description: str = Form(None),
#         pdf_file: UploadFile = File(...),
#         db: Session = Depends(get_session)
# ):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     pdf_bytes = pdf_file.file.read()  # Read the uploaded file
#     expense = Expenseclaim(
#         employee_id=employee_id,
#         expenses_type=expenses_type,
#         bill_number=bill_number,
#         amount=str(amount),
#         description=description,
#         pdf_file=pdf_bytes
#     )
#     db.add(expense)
#     db.commit()
#     db.refresh(expense)
#     return {"message": "Expense claim submitted successfully", "expense_id": expense.id}
#
#
# # ------------------ List Expense Claims ------------------
# @router.get("/expenses/{employee_id}")
# def list_expenses(employee_id: str, current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                   db: Session = Depends(get_session)):
#     emp = db.query(ProfileInformation).filter(ProfileInformation.employee_id == employee_id).first()
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employee not found")
#
#     expenses = db.query(Expenseclaim).filter(Expenseclaim.employee_id == employee_id).all()
#     return [
#         {
#             "id": e.id,
#             "expenses_type": e.expenses_type.value,
#             "bill_number": e.bill_number,
#             "amount": e.amount,
#             "description": e.description
#         }
#         for e in expenses
#     ]
#
#
# # ------------------ Download Expense PDF ------------------
# @router.get("/expenses/{employee_id}/download/{expense_id}")
# def download_expense_pdf(employee_id: str, current_user: Annotated[str, Depends(validate_current_role("admin"))],
#                          expense_id: int, db: Session = Depends(get_session)):
#     expense = db.query(Expenseclaim).filter(
#         Expenseclaim.employee_id == employee_id,
#         Expenseclaim.id == expense_id
#     ).first()
#
#     if not expense:
#         raise HTTPException(status_code=404, detail="Expense claim not found")
#
#     return StreamingResponse(BytesIO(expense.pdf_file), media_type="application/pdf", headers={
#         "Content-Disposition": f"attachment; filename={expense.bill_number}.pdf"
#     })