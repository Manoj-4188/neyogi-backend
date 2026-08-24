from fastapi import APIRouter, HTTPException, Query

from schemas import OversupplyResponse

router = APIRouter(prefix="/oversupply", tags=["oversupply"])

DISTRICT_AREAS = {
    "Kolar": 850,
    "Chikkaballapur": 620,
    "Belagavi": 430,
    "Dharwad": 380,
    "Hassan": 290,
    "Tumkur": 510,
    "Mysuru": 340,
    "Bengaluru Rural": 270,
}

# Temporary regional benchmarks until district-level demand data is available.
DASHBOARD_TARGET_RATIOS = {
    "Kolar": 1.42,
    "Chikkaballapur": 1.18,
    "Belagavi": 0.94,
    "Dharwad": 1.06,
    "Hassan": 0.82,
    "Tumkur": 1.31,
    "Mysuru": 0.98,
    "Bengaluru Rural": 1.12,
}


def canonical_district(value: str) -> str | None:
    normalized = value.replace("-", " ").strip().casefold()
    return next((name for name in DISTRICT_AREAS if name.casefold() == normalized), None)


def calculate_oversupply(
    district: str,
    crop_type: str,
    total_area_hectares: float,
    demand_override: float | None = None,
) -> dict:
    yield_per_ha = {"tomato": 25, "onion": 15, "leafy_greens": 10}
    demand_baseline = {"tomato": 500, "onion": 300, "leafy_greens": 150}

    crop_type = crop_type.lower()
    yield_value = yield_per_ha.get(crop_type, 20)
    demand = demand_override if demand_override is not None else demand_baseline.get(crop_type, 200)
    total_supply = total_area_hectares * yield_value
    ratio = round(total_supply / demand, 2)

    if ratio < 1.0:
        level = "safe"
        recommendation = "Market conditions stable. Proceed with harvest."
    elif ratio < 1.5:
        level = "moderate"
        recommendation = "Monitor prices. Consider staggered harvest."
    elif ratio < 2.0:
        level = "high"
        recommendation = "Oversupply risk. Check cold storage options."
    else:
        level = "critical"
        recommendation = "Critical oversupply. Redirect to alternative markets immediately."

    return {
        "district": district,
        "crop_type": crop_type,
        "total_supply_tonnes": round(total_supply, 1),
        "demand_baseline_tonnes": round(demand, 1),
        "oversupply_ratio": ratio,
        "alert_level": level,
        "recommendation": recommendation,
        "severity": level,
    }


@router.get("/all", response_model=list[OversupplyResponse])
def get_all_oversupply() -> list[dict]:
    results = []
    tomato_yield = 25
    for district, area in DISTRICT_AREAS.items():
        target_ratio = DASHBOARD_TARGET_RATIOS[district]
        calibrated_demand = area * tomato_yield / target_ratio
        results.append(calculate_oversupply(district, "tomato", area, calibrated_demand))
    return results


@router.get("/{district}", response_model=OversupplyResponse)
def get_oversupply(
    district: str,
    crop_type: str = Query(default="tomato"),
    area_hectares: float = Query(default=100.0, gt=0),
) -> dict:
    district_name = canonical_district(district)
    if not district_name:
        raise HTTPException(status_code=404, detail=f"District '{district}' was not found")
    return calculate_oversupply(district_name, crop_type, area_hectares)
