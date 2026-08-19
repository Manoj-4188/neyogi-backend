from fastapi import APIRouter

from ml_models.crop_predictor import predict_crop
from schemas import CropDetectRequest, CropDetectionResponse

router = APIRouter(tags=["crop-detection"])


@router.post("/crop-detect", response_model=CropDetectionResponse)
def detect_crop(data: CropDetectRequest) -> dict:
    try:
        result = predict_crop(data.features.model_dump())
        return {
            "crop_type": str(result["crop_type"]),
            "confidence_score": result["confidence"],
            "probabilities": result["all_probabilities"],
            "source": "random_forest_model",
        }
    except Exception as error:
        return {
            "crop_type": "tomato",
            "confidence_score": 0.85,
            "probabilities": None,
            "source": "mock_fallback",
            "error": str(error),
        }
