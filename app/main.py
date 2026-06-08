import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth_routes import router as auth_router
from app.routes.staff_routes import router as staff_router
from app.routes.admin_user_routes import router as admin_user_router
from app.routes.admin_attendance_routes import router as admin_attendance_router


# Load .env from backend root explicitly
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_cors_origins_from_env():
    raw_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://localhost:8000",
    )

    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins


cors_origins = get_cors_origins_from_env()

# print("======================================")
# print("Loaded .env from:", ENV_PATH)
# print("CORS_ALLOWED_ORIGINS:", cors_origins)
# print("======================================")


app = FastAPI(
    title="ScanX Web Check-In API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "cors_origins": cors_origins,
    }


app.include_router(auth_router)
app.include_router(staff_router)
app.include_router(admin_user_router)
app.include_router(admin_attendance_router)