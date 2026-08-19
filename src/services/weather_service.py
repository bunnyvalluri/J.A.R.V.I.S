"""
weather_service.py — Geolocation & Weather Forecasting Service
===============================================================
"""

import requests
import geocoder

WMO_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def get_location():
    """Detect current location coordinates and city name."""
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return {
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "city": data.get("city", "Unknown City"),
                    "country": data.get("country", "")
                }
    except Exception:
        pass

    try:
        g = geocoder.ip('me')
        if g and g.latlng:
            return {
                "lat": g.latlng[0],
                "lon": g.latlng[1],
                "city": g.city or "Your Location",
                "country": g.country or ""
            }
    except Exception:
        pass

    return {"lat": 28.6139, "lon": 77.2090, "city": "Current Location", "country": ""}


def get_weather(city_name=None):
    """Fetch current real-time weather using Open-Meteo API."""
    loc = get_location()
    lat = loc["lat"]
    lon = loc["lon"]
    city = loc["city"]

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current", {})
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind = current.get("wind_speed_10m")
            code = current.get("weather_code", 0)
            condition = WMO_CODE_MAP.get(code, "Clear")

            spoken_summary = f"In {city}, the weather is currently {condition.lower()} with a temperature of {temp}°C, humidity at {humidity}%, and wind speed around {wind} km/h."
            display_summary = f"{condition} | {temp}°C | Humidity: {humidity}% | Wind: {wind} km/h ({city})"

            return {
                "success": True,
                "city": city,
                "temperature": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind,
                "spoken": spoken_summary,
                "display": display_summary
            }
    except Exception:
        pass

    # Fallback to wttr.in
    try:
        resp = requests.get(f"https://wttr.in/{city}?format=%C+%t+%h+%w", timeout=4)
        if resp.status_code == 200:
            wttr_text = resp.text.strip()
            return {
                "success": True,
                "city": city,
                "spoken": f"The weather in {city} is currently {wttr_text}.",
                "display": f"{wttr_text} ({city})"
            }
    except Exception:
        pass

    return {
        "success": False,
        "spoken": "I am currently unable to retrieve weather data.",
        "display": "Weather service unavailable"
    }
