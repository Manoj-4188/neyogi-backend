import os

import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "neyogi_crop_model.pkl")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURES_PATH)


def predict_crop(feature_dict: dict):
    """Predict a crop from vegetation and spectral feature values."""
    features = [feature_dict.get(column, 0.0) for column in feature_columns]
    feature_vector = np.array(features).reshape(1, -1)

    prediction = model.predict(feature_vector)[0]
    probabilities = model.predict_proba(feature_vector)[0]
    confidence = round(float(max(probabilities)), 3)

    return {
        "crop_type": prediction,
        "confidence": confidence,
        "all_probabilities": {
            str(cls): round(float(probability), 3)
            for cls, probability in zip(model.classes_, probabilities)
        },
    }


def predict_batch(features_list: list):
    """Predict crops for a list of feature dictionaries."""
    return [predict_crop(feature_dict) for feature_dict in features_list]
