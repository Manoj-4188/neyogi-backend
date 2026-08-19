from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import AlertSent
from schemas import AlertResponse, SendAlertRequest, SendAlertResponse

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    crop_type: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AlertSent]:
    statement = select(AlertSent).order_by(AlertSent.alert_date.desc(), AlertSent.id.desc())
    if crop_type:
        statement = statement.where(AlertSent.crop_type == crop_type.lower())
    if date_from:
        statement = statement.where(AlertSent.alert_date >= date_from)
    if date_to:
        statement = statement.where(AlertSent.alert_date <= date_to)
    return list(db.scalars(statement).all())


@router.post("/alert/send", response_model=SendAlertResponse)
def send_alert(payload: SendAlertRequest, db: Session = Depends(get_db)) -> SendAlertResponse:
    farmers_notified = 25 if payload.severity == "moderate" else 50 if payload.severity == "high" else 75
    alert = AlertSent(
        district=payload.district,
        crop_type=payload.crop_type.lower(),
        oversupply_ratio=payload.oversupply_ratio,
        severity=payload.severity.lower(),
        alert_date=date.today(),
        farmers_notified=farmers_notified,
        action_taken="FPO coordination alert sent",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return SendAlertResponse(success=True, alert_id=alert.id, farmers_notified=farmers_notified)
