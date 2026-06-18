from datetime import datetime

import requests

from config import (
    RAIN_JSON
)

from utils import (
    write_json
)


CATCHMENT_URL = (
    "https://openaccess.pf.api.met.ie/"
    "metno-wdb2ts/locationforecast"
    "?lat=54.04"
    ";long=-9.62"
)


def rainfall_value(entry):

    try:

        return float(

            entry["data"]
            ["next_1_hours"]
            ["details"]
            ["precipitation_amount"]

        )

    except Exception:

        return 0.0


def fetch_rainfall():

    try:

        response = requests.get(
            CATCHMENT_URL,
            timeout=60
        )

        response.raise_for_status()

        payload = response.json()

        timeseries = (
            payload["properties"]
            ["timeseries"]
        )

        series = []

        for item in timeseries:

            rain = rainfall_value(
                item
            )

            series.append({

                "timestamp":
                item["time"],

                "rain_mm":
                rain
            })

        past24 = 0.0
        past48 = 0.0

        next6 = sum(
            rainfall_value(x)
            for x in timeseries[:6]
        )

        next12 = sum(
            rainfall_value(x)
            for x in timeseries[:12]
        )

        next24 = sum(
            rainfall_value(x)
            for x in timeseries[:24]
        )

        next48 = sum(
            rainfall_value(x)
            for x in timeseries[:48]
        )

        result = {

            "series":
            series,

            "summary": {

                "past24h_mm":
                round(
                    past24,
                    1
                ),

                "past48h_mm":
                round(
                    past48,
                    1
                ),

                "next6h_mm":
                round(
                    next6,
                    1
                ),

                "next12h_mm":
                round(
                    next12,
                    1
                ),

                "next24h_mm":
                round(
                    next24,
                    1
                ),

                "next48h_mm":
                round(
                    next48,
                    1
                )
            }
        }

        write_json(
            RAIN_JSON,
            result
        )

        return {
            "ok": True
        }

    except Exception as e:

        write_json(
            RAIN_JSON,
            {}
        )

        return {
            "ok": False,
            "error": str(e)
        }


if __name__ == "__main__":
    print(
        fetch_rainfall()
    )
