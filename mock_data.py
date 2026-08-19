from datetime import date, timedelta
from math import sin

DISTRICTS = {
    "Kolar": {"crop_type": "tomato", "supply": 84, "demand": 59, "lat": 13.1358, "lng": 78.1294},
    "Chikkaballapur": {"crop_type": "tomato", "supply": 71, "demand": 60, "lat": 13.4355, "lng": 77.7315},
    "Belagavi": {"crop_type": "onion", "supply": 58, "demand": 62, "lat": 15.8497, "lng": 74.4977},
    "Dharwad": {"crop_type": "potato", "supply": 63, "demand": 59, "lat": 15.4589, "lng": 75.0078},
    "Hassan": {"crop_type": "potato", "supply": 46, "demand": 56, "lat": 13.0068, "lng": 76.1004},
    "Tumkur": {"crop_type": "tomato", "supply": 79, "demand": 60.3, "lat": 13.3379, "lng": 77.1173},
    "Mysuru": {"crop_type": "onion", "supply": 51, "demand": 52.04, "lat": 12.2958, "lng": 76.6394},
    "Bengaluru Rural": {"crop_type": "onion", "supply": 68, "demand": 60.7143, "lat": 13.2847, "lng": 77.586},
}


def canonical_district(value: str) -> str | None:
    normalized = value.replace("-", " ").strip().casefold()
    return next((name for name in DISTRICTS if name.casefold() == normalized), None)

MARKETS = [
    {"market_name": "Kolar APMC", "district": "Kolar", "price": {"tomato": 2250, "onion": 1900, "potato": 1750}, "distance_km": 12},
    {"market_name": "Yeshwanthpur APMC", "district": "Bengaluru Rural", "price": {"tomato": 2420, "onion": 2140, "potato": 1880}, "distance_km": 54},
    {"market_name": "Chikkaballapur APMC", "district": "Chikkaballapur", "price": {"tomato": 2310, "onion": 1860, "potato": 1810}, "distance_km": 18},
    {"market_name": "Dharwad APMC", "district": "Dharwad", "price": {"tomato": 2080, "onion": 2210, "potato": 1920}, "distance_km": 110},
    {"market_name": "Belagavi APMC", "district": "Belagavi", "price": {"tomato": 2110, "onion": 2290, "potato": 1860}, "distance_km": 235},
    {"market_name": "Mysuru APMC", "district": "Mysuru", "price": {"tomato": 2180, "onion": 2070, "potato": 1830}, "distance_km": 145},
    {"market_name": "Hassan APMC", "district": "Hassan", "price": {"tomato": 2140, "onion": 2010, "potato": 1890}, "distance_km": 165},
    {"market_name": "Tumkur APMC", "district": "Tumkur", "price": {"tomato": 2280, "onion": 1980, "potato": 1790}, "distance_km": 72},
]


def severity_for_ratio(ratio: float) -> str:
    if ratio < 1.0:
        return "safe"
    if ratio <= 1.5:
        return "moderate"
    if ratio <= 2.0:
        return "high"
    return "critical"


def price_history(district: str | None = None) -> list[dict]:
    district = canonical_district(district) if district else None
    offset = list(DISTRICTS).index(district) if district in DISTRICTS else 0
    today = date.today()
    points = []
    for days_ago in range(89, -1, -1):
        current = today - timedelta(days=days_ago)
        wave = sin((90 - days_ago + offset) / 8)
        points.append({
            "date": current,
            "tomato_price": round(2200 + offset * 18 + wave * 95 + (90 - days_ago) * 1.2, 2),
            "onion_price": round(1900 + offset * 16 + wave * 70 + (90 - days_ago) * 0.8, 2),
            "potato_price": round(1750 + offset * 12 + wave * 45 - (90 - days_ago) * 0.3, 2),
        })
    return points


def storage_for_district(district: str) -> list[dict]:
    district = canonical_district(district)
    info = DISTRICTS.get(district) if district else None
    if not info:
        return []
    names = ["AgriChill Hub", "FPO Cold Chain", "Karnataka Fresh Store", "Harvest Shield"]
    return [{
        "name": f"{district} {names[index]}",
        "latitude": info["lat"] + (index + 1) * 0.025,
        "longitude": info["lng"] + (index % 2 - 0.5) * 0.04,
        "capacity_tonnes": 500 + index * 275,
        "cost_per_day_per_tonne": 4.5 + index * 0.35,
        "crops_supported": "tomato,onion,potato" if index % 2 == 0 else "onion,potato",
        "contact_number": f"+91 80 45{index} 78{index}90",
    } for index in range(4)]
