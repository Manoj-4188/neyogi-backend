from datetime import date

from pydantic import BaseModel, Field


class OversupplyResponse(BaseModel):
    district: str
    crop_type: str
    oversupply_ratio: float
    severity: str
    alert_level: str


class BestMarketRequest(BaseModel):
    district: str
    crop_type: str
    quantity_quintals: float = Field(gt=0)


class BestMarketResult(BaseModel):
    market_name: str
    price_per_quintal: float
    transport_cost: float
    net_profit: float
    distance_km: float


class PricePoint(BaseModel):
    date: date
    tomato_price: float
    onion_price: float
    potato_price: float


class ColdStorageResult(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_km: float
    capacity_tonnes: float
    cost_per_day: float
    crops_supported: list[str]
    contact_number: str
    storage_cost_total: float
    net_benefit: float


class AlertResponse(BaseModel):
    id: int
    district: str
    crop_type: str
    oversupply_ratio: float
    severity: str
    alert_date: date
    farmers_notified: int
    action_taken: str

    model_config = {"from_attributes": True}


class SendAlertRequest(BaseModel):
    district: str
    crop_type: str
    oversupply_ratio: float = Field(gt=0)
    severity: str


class SendAlertResponse(BaseModel):
    success: bool
    alert_id: int
    farmers_notified: int


class CropDetectionRequest(BaseModel):
    latitude: float
    longitude: float
    date: date


class CropDetectionResponse(BaseModel):
    crop_type: str
    confidence_score: float
    ndvi_value: float


class HarvestPredictionRequest(BaseModel):
    farm_id: int = Field(gt=0)


class HarvestPredictionResponse(BaseModel):
    farm_id: int
    predicted_harvest_date: date
    confidence_days: int
    is_high_confidence: bool
