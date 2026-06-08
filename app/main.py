from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth_routes import router as auth_router
from app.routes.staff_routes import router as staff_router
from app.routes.admin_user_routes import router as admin_user_router
from app.routes.admin_attendance_routes import router as admin_attendance_router


app = FastAPI(
    title="ScanX Web Check-In API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
    }


app.include_router(auth_router)
app.include_router(staff_router)
app.include_router(admin_user_router)
app.include_router(admin_attendance_router)