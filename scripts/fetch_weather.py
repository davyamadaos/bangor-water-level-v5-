import requests
from datetime import datetime

from config import WEATHER_JSON
from utils import write_json


WEATHER_URL = (
    "https://openaccess.pf.api.met.ie/"
    "metno-wdb2ts/locationforecast"
    "?lat=54.12084559360346"
    ";long=-9.575250065156835"
)


def safe_float(v):

    try:
        return float(v)
    except Exception:
        return None


def fetch_weather():

    try:

        response = requests.get(
            WEATHER_URL,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        timeseries = (
            data["properties"]
            ["timeseries"]
        )

        current = {}

        forecast = []

        if timeseries:

            first = timeseries[0]

            instant = (
                first["data"]
                .get("instant", {})
                .get("details", {})
            )

            current = {

                "timestamp":
                first["time"],

                "temperature_c":
                safe_float(
                    instant.get(
                        "air_temperature"
                    )
                ),

                "wind_speed_kmh":
                round(
                    safe_float(
                        instant.get(
                            "wind_speed"
                        )
                    ) * 3.6,
                    1
                )
                if instant.get(
                    "wind_speed"
                ) is not None
                else None,

                "wind_direction":
                instant.get(
                    "wind_from_direction"
                ),

                "condition":
                "Forecast"
            }

        for item in timeseries[:56:8]:

            details = (
                item["data"]
                .get("instant", {})
                .get("details", {})
            )

            forecast.append({

                "day":
                item["time"][:10],

                "temp_max":
                details.get(
                    "air_temperature"
                ),

                "temp_min":
                details.get(
                    "air_temperature"
                ),

                "rain_mm":
                0,

                "condition":
                "Forecast"
            })

        result = {

            "current":
            current,

            "forecast":
            forecast
        }

        write_json(
            WEATHER_JSON,
            result
        )

        return {
            "ok": True
        }

    except Exception as e:

        write_json(
            WEATHER_JSON,
            {}
        )

        return {
            "ok": False,
            "error": str(e)
        }


if __name__ == "__main__":
    print(
        fetch_weather()
    )
