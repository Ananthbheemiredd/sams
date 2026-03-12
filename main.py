from dotenv import load_dotenv

from app.database.base import Base, engine

# from app.routers.notification_router import

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.secret_initializer import ensure_api_secret

from app.routers import (
    auth_router,
    mfa_router,
    role_based,
    pre_registration_router,
    application_router,
    exam_router,
    admissions_router,
    fee_router,
    hostel_router,
    session_router, academic_router,  payroll_router, school_router, branch_router,
    payroll_management_router, profile_router,
)

# -------------------------------------------------
# ENSURE SECRET KEY
# -------------------------------------------------
ensure_api_secret()

# -------------------------------------------------
# FASTAPI APP (Swagger ENABLED)
# -------------------------------------------------
app = FastAPI(
    title="School Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "persistAuthorization": True
    },
)

# -------------------------------------------------
# DATABASE ENGINE (NO SIDE EFFECTS)
# -------------------------------------------------
# engine = create_async_engine(
#     settings.DATABASE_URL,
#     echo=False,
#     future=True,
# )

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# -------------------------------------------------
# CORS CONFIG (CORRECT)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://192.168.0.118:5173",
        "http://192.168.1.28:5173",
        "http://192.168.0.107:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# ROUTERS
# -------------------------------------------------
app.include_router(school_router.router)
app.include_router(branch_router.router)
app.include_router(auth_router.router)
app.include_router(mfa_router.router)
app.include_router(role_based.router)
app.include_router(pre_registration_router.router)
app.include_router(application_router.router)
app.include_router(profile_router.router)
app.include_router(exam_router.router)
app.include_router(admissions_router.router)
app.include_router(fee_router.router)
app.include_router(hostel_router.router)
app.include_router(session_router.router)
app.include_router(academic_router.router)

# app.include_router(payroll_router.router)
app.include_router(payroll_management_router.router)
# -------------------------------------------------
# ROOT (HEALTH CHECK)
# -------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "OK",
        "message": "School Management System running 🚀",
        "docs": "/docs"
    }












