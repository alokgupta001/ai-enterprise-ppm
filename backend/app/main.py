from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import assessment
from app.models import organization
from app.models import user
from app.models import project
from app.core.config import CORS_ORIGINS, ENV
from app.routers.organization import router as organization_router
from app.routers.assessment import router as assessment_router
from app.routers.auth import router as auth_router
from app.routers.project import router as project_router
from app.routers.assistant import router as assistant_router

app = FastAPI(
    title="AI Enterprise PPM",
    version="1.0.0"
)

# CORS (frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(assessment_router)
app.include_router(project_router)
app.include_router(assistant_router)

# Health Check Route
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "AI Enterprise PPM Backend"
    }

# Create DB Tables (DEV ONLY)
@app.on_event("startup")
def startup():
    if ENV != "production":
        Base.metadata.create_all(bind=engine)