from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import engine, Base
from app.api import health, machines, predict, recommend, predictions, recommendations

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed machines
    Base.metadata.create_all(bind=engine)
    from app.db.session import SessionLocal
    from app.models.models import Machine
    db = SessionLocal()
    try:
        if db.query(Machine).count() == 0:
            db.add_all([
                Machine(machine_id=f"M-{i:03d}", name=f"CNC Unit {i}", machine_type="CNC", location=f"Bay {i}")
                for i in range(1, 6)
            ])
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Industrial AI Predictive Maintenance Platform — by Anansh",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(machines.router, prefix="/machines", tags=["Machines"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(recommend.router, tags=["Recommendation"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
