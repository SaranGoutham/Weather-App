from fastapi import APIRouter, HTTPException, Query
import httpx

from ..core.config import settings

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/current")
async def current_weather(
    q: str | None = Query(default=None, description="City name, e.g. 'Hyderabad'"),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    units: str = Query(default=settings.DEFAULT_UNITS)
):
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

        # return a tidy payload (great for learning + frontend)
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
