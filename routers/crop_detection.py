from fastapi import APIRouter

from schemas import CropDetectionRequest, CropDetectionResponse

router = APIRouter(tags=["crop-detection"])


@router.post("/crop-detect", response_model=CropDetectionResponse)
def detect_crop(payload: CropDetectionRequest) -> CropDetectionResponse:
    del payload
    return CropDetectionResponse(crop_type="tomato", confidence_score=0.91, ndvi_value=0.68)
