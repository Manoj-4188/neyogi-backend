from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from mock_data import MARKETS, price_history
from schemas import BestMarketRequest, BestMarketResult, PricePoint

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


@router.get("/market-prices", response_model=list[PricePoint])
def get_market_prices(
    district: str | None = Query(default=None),
    crop_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PricePoint]:
    del db, crop_type
    return [PricePoint(**point) for point in price_history(district)]
