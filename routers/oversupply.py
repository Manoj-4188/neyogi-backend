from fastapi import APIRouter, HTTPException

from mock_data import DISTRICTS, canonical_district, severity_for_ratio
from schemas import OversupplyResponse

router = APIRouter(prefix="/oversupply", tags=["oversupply"])


def build_response(district: str, info: dict) -> OversupplyResponse:
    ratio = round(info["supply"] / info["demand"], 2)
    severity = severity_for_ratio(ratio)
    return OversupplyResponse(
        district=district,
        crop_type=info["crop_type"],
        oversupply_ratio=ratio,
        severity=severity,
        alert_level=severity.upper(),
    )


@router.get("/all", response_model=list[OversupplyResponse])
def get_all_oversupply() -> list[OversupplyResponse]:
    return [build_response(district, info) for district, info in DISTRICTS.items()]


@router.get("/{district}", response_model=OversupplyResponse)
def get_oversupply(district: str) -> OversupplyResponse:
    district = canonical_district(district)
    info = DISTRICTS.get(district) if district else None
    if not info:
        raise HTTPException(status_code=404, detail=f"District '{district}' was not found")
    return build_response(district, info)
