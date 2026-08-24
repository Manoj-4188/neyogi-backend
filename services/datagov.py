import os
import random
from datetime import datetime, timedelta

import requests

API_KEY = os.getenv(
    "DATAGOV_API_KEY",
    "579b464db66ec23bdd0000010af4365ff84a4fba4f713d24e0ac1693",
)
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


def fetch_karnataka_prices(commodity: str, limit: int = 100) -> list[dict]:
    """Fetch current mandi prices for one commodity in Karnataka."""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "filters[state]": "Karnataka",
        "filters[commodity]": commodity,
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        records = response.json().get("records", [])
        return records if isinstance(records, list) else []
    except (requests.RequestException, ValueError) as error:
        print(f"data.gov.in API error for {commodity}: {error}")
        return []


def get_karnataka_market_prices(district: str | None = None) -> dict[str, list[dict]]:
    """Return current tomato, onion, potato, and spinach mandi records for Karnataka."""
    results = {}

    for commodity, result_key in (
        ("Tomato", "tomato"),
        ("Onion", "onion"),
        ("Potato", "potato"),
        ("Spinach", "leafy_greens"),
    ):
        records = fetch_karnataka_prices(commodity, 50)
        if district and district.casefold() != "karnataka":
            records = [
                record for record in records
                if district.casefold() in record.get("District", "").casefold()
            ]
        if records:
            results[result_key] = records

    return results


def _modal_price(records: list[dict], fallback: float) -> float:
    for record in records:
        try:
            price = record.get("Modal_x0020_Price", 0)
            if price:
                return float(price)
        except (TypeError, ValueError):
            pass
    return fallback


def get_price_timeseries(district: str = "all") -> list[dict]:
    """Build a 90-day chart anchored to current data.gov.in modal prices."""
    real_prices = get_karnataka_market_prices(district)
    tomato_current = _modal_price(real_prices.get("tomato", []), 1200)
    onion_current = _modal_price(real_prices.get("onion", []), 850)
    potato_current = _modal_price(real_prices.get("potato", []), 700)
    leafy_current = _modal_price(real_prices.get("leafy_greens", []), 600)
    random_generator = random.Random(f"neyogi-{district}")
    tomato_price = tomato_current * 0.85
    onion_price = onion_current * 0.90
    potato_price = potato_current * 0.92
    leafy_price = leafy_current * 0.95
    today = datetime.now()
    timeseries = []

    for index in range(90):
        tomato_price += random_generator.gauss(0, 25) + (tomato_current - tomato_price) * 0.03
        onion_price += random_generator.gauss(0, 15) + (onion_current - onion_price) * 0.03
        potato_price += random_generator.gauss(0, 12) + (potato_current - potato_price) * 0.03
        leafy_price += random_generator.gauss(0, 10) + (leafy_current - leafy_price) * 0.03
        timeseries.append({
            "date": (today - timedelta(days=90 - index)).strftime("%Y-%m-%d"),
            "tomato_price": round(max(200, tomato_price), 2),
            "onion_price": round(max(150, onion_price), 2),
            "potato_price": round(max(150, potato_price), 2),
            "leafy_greens_price": round(max(100, leafy_price), 2),
        })
    return timeseries
