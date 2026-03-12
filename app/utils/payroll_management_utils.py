# =====================================================================================
# IMPORTS (ONLY WHAT YOU HAVE)
# =====================================================================================

import json
import logging
from io import BytesIO
from pathlib import Path
from datetime import date
from typing import Dict, List, Optional

import PyPDF2
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.profile_information import ProfileInformation
from app.models.payroll_management import SalaryPolicy1, TaxSlab1

async def get_employee_profile(db: AsyncSession, employee_id: str) -> ProfileInformation:
    result = await db.execute(
        select(ProfileInformation).where(ProfileInformation.employee_id == employee_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise ValueError(f"Employee profile not found: {employee_id}")
    return profile

def calculate_annual_tax_flat(annual_ctc: float, slab_ranges: List[Dict]) -> float:
    for slab in slab_ranges:
        if slab["lower_limit"] <= annual_ctc <= slab["upper_limit"]:
            return round(annual_ctc * slab["rate"], 2)
    return 0.0

async def compute_salary_components(
    db: AsyncSession,
    annual_ctc: float,
    regime: str,
    lop_days: int = 0,
    total_working_days: int = 30,
    bonus: float = 0.0,
) -> Dict:

    result = await db.execute(
        select(SalaryPolicy1).where(SalaryPolicy1.is_active == True)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise ValueError("No active salary policy found")

    monthly_ctc = round(annual_ctc / 12, 2)

    basic = 0.0
    for c in policy.components:
        if c.get("component_name") == "basic_salary":
            basic = round(monthly_ctc * (c.get("percentage", 0) / 100), 2)
            break

    earnings = basic + bonus
    daily_salary = monthly_ctc / total_working_days
    lop_amount = round(lop_days * daily_salary, 2)

    today = date.today()
    result = await db.execute(
        select(TaxSlab1)
        .where(
            TaxSlab1.regime == regime,
            TaxSlab1.is_active == 1,
            TaxSlab1.effective_from <= today,
        )
        .order_by(TaxSlab1.effective_from.desc())
    )
    slab = result.scalar_one_or_none()

    tax = 0.0
    if slab:
        tax = calculate_annual_tax_flat(annual_ctc, slab.slab_ranges) / 12

    net_salary = round(earnings - lop_amount - tax, 2)

    return {
        "monthly_ctc": monthly_ctc,
        "basic_salary": basic,
        "bonus": bonus,
        "lop_amount": lop_amount,
        "tax_deductions": tax,
        "net_salary": net_salary,
        "total_ctc": annual_ctc,
    }

def load_config() -> Dict:
    config_path = Path(__file__).resolve().parent.parent / "config" / "payslip_settings.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_password(emp_data: Dict, default: str = "1234") -> str:
    doj = emp_data.get("doj", "")
    emp_id = emp_data.get("emp_id", "")
    if doj:
        digits = "".join(filter(str.isdigit, doj))[-4:]
        return f"{emp_id}{digits}"
    return default

def generate_payslip_pdf(emp_data: Dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "Salary Slip")

    c.setFont("Helvetica", 10)
    y = height - 90
    for k, v in emp_data.items():
        c.drawString(40, y, f"{k}: {v}")
        y -= 14

    c.showPage()
    c.save()

    buffer.seek(0)
    reader = PyPDF2.PdfReader(buffer)
    writer = PyPDF2.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(generate_password(emp_data))

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()

