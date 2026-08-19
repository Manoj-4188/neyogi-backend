from datetime import date, timedelta

from fastapi import APIRouter

from schemas import HarvestPredictionRequest, HarvestPredictionResponse

router = APIRouter(tags=["harvest"])


@router.post("/harvest-predict", response_model=HarvestPredictionResponse)
def predict_harvest(payload: HarvestPredictionRequest) -> HarvestPredictionResponse:
    return HarvestPredictionResponse(
        farm_id=payload.farm_id,
        predicted_harvest_date=date.today() + timedelta(days=14),
        confidence_days=7,
        is_high_confidence=True,
    )
