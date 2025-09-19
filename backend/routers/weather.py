# backend/routers/weather.py
from fastapi import APIRouter, HTTPException, Query, Request
import httpx
from collections import defaultdict

from ..core.config import settings
from ..core.ratelimit_inmemory import rate_limit_ip

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/current")
async def current_weather(
    request: Request,
    q: str | None = Query(default=None, description="City name, e.g. 'Hyderabad'"),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    units: str = Query(default=settings.DEFAULT_UNITS),
):
    rate_limit_ip(request)  # in-memory per-IP limit

    if not settings.OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY")

    params = {"appid": settings.OPENWEATHER_API_KEY, "units": units}
    if q:
        params["q"] = q
        path = "weather"
    elif lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
        path = "weather"
    else:
        raise HTTPException(status_code=400, detail="Provide 'q' or 'lat' & 'lon'.")

    url = f"{settings.OPENWEATHER_BASE_URL}/{path}"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise HTTPException(status_code=r.status_code, detail=detail)

        data = r.json()
        return {
            "location": {
                "name": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "coord": data.get("coord"),
            },
            "weather": {
                "main": (data.get("weather") or [{}])[0].get("main"),
                "description": (data.get("weather") or [{}])[0].get("description"),
                "icon": (data.get("weather") or [{}])[0].get("icon"),
                "temp": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
            },
            "wind": data.get("wind"),
            "visibility": data.get("visibility"),
        }

@router.get("/forecast")
async def forecast(
    request: Request,
    q: str | None = Query(default=None, description="City name, e.g. 'Hyderabad'"),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    units: str = Query(default=settings.DEFAULT_UNITS),
):
    rate_limit_ip(request)  # in-memory per-IP limit

    if not settings.OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY")

    async with httpx.AsyncClient(timeout=10) as client:
        # Resolve coordinates if only q is provided
        if q and (lat is None or lon is None):
            r0 = await client.get(
                f"{settings.OPENWEATHER_BASE_URL}/weather",
                params={"q": q, "appid": settings.OPENWEATHER_API_KEY, "units": units},
            )
            if r0.status_code != 200:
                raise HTTPException(status_code=r0.status_code, detail=r0.json())
            w0 = r0.json()
            lat, lon = w0["coord"]["lat"], w0["coord"]["lon"]

        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail="Provide 'q' or 'lat' & 'lon'.")

        # 5-day / 3-hour forecast
        r = await client.get(
            f"{settings.OPENWEATHER_BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": units},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.json())

        data = r.json()  # has 'list' and 'city'

        # Aggregate to daily min/max
        buckets = defaultdict(lambda: {"min": float("inf"), "max": float("-inf")})
        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]  # "YYYY-MM-DD"
            t = item["main"]["temp"]
            buckets[date]["min"] = min(buckets[date]["min"], t)
            buckets[date]["max"] = max(buckets[date]["max"], t)

        days_sorted = sorted(buckets.keys())[:days]
        return {
            "location": {
                "name": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country"),
                "coord": {"lat": lat, "lon": lon},
            },
            "units": units,
            "daily": [{"date": d, "temp_min": buckets[d]["min"], "temp_max": buckets[d]["max"]} for d in days_sorted],
        }
