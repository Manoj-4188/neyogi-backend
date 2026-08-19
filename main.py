from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401 - registers all ORM models with Base.metadata
from database import Base, SessionLocal, engine
from models import AlertSent
from mock_data import DISTRICTS, severity_for_ratio
from routers import alerts, cold_storage, crop_detection, harvest, market, oversupply


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_alerts()
    yield


def seed_alerts() -> None:
    with SessionLocal() as db:
        if db.query(AlertSent).first() is not None:
            return
        for district, info in DISTRICTS.items():
            ratio = round(info["supply"] / info["demand"], 2)
            db.add(AlertSent(
                district=district,
                crop_type=info["crop_type"],
                oversupply_ratio=ratio,
                severity=severity_for_ratio(ratio),
                alert_date=date.today(),
                farmers_notified=24,
                action_taken="Monitoring and FPO coordination",
            ))
        db.commit()


app = FastAPI(title="NEYOGI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crop_detection.router, prefix="/api")
app.include_router(harvest.router, prefix="/api")
app.include_router(oversupply.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(cold_storage.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "NEYOGI backend running"}
