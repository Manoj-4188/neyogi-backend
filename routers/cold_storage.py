from math import sqrt

from fastapi import APIRouter, HTTPException, Query

from mock_data import DISTRICTS, MARKETS, canonical_district, storage_for_district
from schemas import ColdStorageResult

router = APIRouter(prefix="/cold-storage", tags=["cold-storage"])


@router.get("/{district}", response_model=list[ColdStorageResult])
def get_cold_storage(
    district: str,
    quantity_tonnes: float = Query(default=10, gt=0),
    storage_days: int = Query(default=7, gt=0),
) -> list[ColdStorageResult]:
    district = canonical_district(district)
    origin = DISTRICTS.get(district) if district else None
    facilities = storage_for_district(district)
    if not origin:
        raise HTTPException(status_code=404, detail=f"District '{district}' was not found")
    current_price = next((market["price"].get(origin["crop_type"], 0) for market in MARKETS if market["district"] == district), 2000)
    recovery_price = current_price * 1.12
    results = []
    for facility in facilities:
        distance = sqrt(((facility["latitude"] - origin["lat"]) * 111) ** 2 + ((facility["longitude"] - origin["lng"]) * 107) ** 2)
        storage_cost_total = round(facility["cost_per_day_per_tonne"] * quantity_tonnes * storage_days, 2)
        net_benefit = round((recovery_price - current_price) * quantity_tonnes - storage_cost_total, 2)
        results.append(ColdStorageResult(
            name=facility["name"],
            latitude=facility["latitude"],
            longitude=facility["longitude"],
            distance_km=round(distance, 1),
            capacity_tonnes=facility["capacity_tonnes"],
            cost_per_day=facility["cost_per_day_per_tonne"],
            crops_supported=facility["crops_supported"].split(","),
            contact_number=facility["contact_number"],
            storage_cost_total=storage_cost_total,
            net_benefit=net_benefit,
        ))
    return results
