from datetime import datetime

from fastapi import APIRouter
import requests

from services.datagov import API_KEY, BASE_URL, get_karnataka_market_prices, get_price_timeseries
from mock_data import MARKETS
from schemas import BestMarketRequest, BestMarketResult

router = APIRouter(tags=["market"])
@router.post("/best-market", response_model=list[BestMarketResult])
def best_market(payload: BestMarketRequest) -> list[BestMarketResult]:
    options = []
    for market in MARKETS:
        price = market["price"].get(payload.crop_type.lower(), 0)
        if not price:
            continue
        transport_cost = round(market["distance_km"] * 2.5, 2)
        options.append(BestMarketResult(
            market_name=market["market_name"],
            price_per_quintal=price,
            transport_cost=transport_cost,
            net_profit=round(price - transport_cost, 2),
            distance_km=market["distance_km"],
        ))
    return sorted(options, key=lambda item: item.net_profit, reverse=True)[:3]


@router.get("/market-prices")
def get_market_prices(
    district: str = "all",
    crop_type: str | None = None,
) -> dict:
    del crop_type
    return {
        "district": district,
        "data": get_price_timeseries(district),
        "source": "data.gov.in - Ministry of Agriculture",
    }


@router.get("/market-prices/current")
def get_current_prices(district: str = "Karnataka") -> dict:
    return {
        "district": district,
        "prices": get_karnataka_market_prices(district),
        "source": "data.gov.in - Ministry of Agriculture",
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/market-prices/debug")
def debug_prices() -> dict:
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 5,
        "filters[state]": "Karnataka",
        "filters[commodity]": "Tomato",
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        return {"status": "error", "message": str(error)}
