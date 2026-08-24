import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

AGMARKNET_URL = "https://agmarknet.gov.in/PriceAndArrivals/CommodityDailyStateWise.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _clean_price(value: str) -> str:
    return re.sub(r"[^0-9.]", "", value)


def fetch_live_price(
    commodity: str,
    state: str = "Karnataka",
    market: str = "Bangalore",
) -> list[dict] | None:
    """Scrape today's top mandi price rows from Agmarknet."""
    today = datetime.now().strftime("%d-%b-%Y")
    params = {
        "Tx_Commodity": commodity,
        "Tx_State": state,
        "Tx_District": "0",
        "Tx_Market": "0",
        "DateFrom": today,
        "DateTo": today,
        "Fr_Date": today,
        "To_Date": today,
        "Tx_Trend": "0",
        "Tx_CommodityHead": commodity,
        "Tx_StateHead": state,
        "Tx_DistrictHead": "0",
        "Tx_MarketHead": "0",
    }
    try:
        response = requests.get(AGMARKNET_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "cphBody_GridPriceData"})
        if not table:
            return None

        prices = []
        for row in table.find_all("tr")[1:11]:
            columns = row.find_all("td")
            if len(columns) < 8:
                continue
            row_market = columns[2].get_text(strip=True)
            if market and market.casefold() not in row_market.casefold() and market != "Bangalore":
                continue
            prices.append({
                "state": columns[0].get_text(strip=True),
                "district": columns[1].get_text(strip=True),
                "market": row_market,
                "commodity": columns[3].get_text(strip=True),
                "variety": columns[4].get_text(strip=True),
                "min_price": _clean_price(columns[5].get_text(strip=True)),
                "max_price": _clean_price(columns[6].get_text(strip=True)),
                "modal_price": _clean_price(columns[7].get_text(strip=True)),
                "date": columns[8].get_text(strip=True) if len(columns) > 8 else today,
            })
        return prices
    except (requests.RequestException, ValueError) as error:
        print(f"Agmarknet scrape error for {commodity}: {error}")
        return None


def get_karnataka_prices_all() -> dict[str, list[dict]]:
    """Get current tomato, onion, and spinach prices for Karnataka."""
    results = {}
    for crop in ("Tomato", "Onion", "Spinach"):
        records = fetch_live_price(crop, "Karnataka")
        if records:
            crop_key = "leafy_greens" if crop == "Spinach" else crop.lower()
            results[crop_key] = records
    return results
